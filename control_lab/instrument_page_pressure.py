from .instrument_math import page,pure_request,pressure_from_token
from .core import score_content

PAGE=page('pressure','Grammar pressure','Same answer. Very different pressure.',
    'Two grammars can leave the same 60/40 choice while discarding radically different amounts of model probability.',
    'At each native prefix, log Z = raw selected logprob minus log masked selected probability. Temperature is exactly 1 and no other operator is enabled. Pressure is KL(q || p) for this mask, not the probability of the entire grammar language.',
    ['native mass','KL divergence','GBNF as sensor'],
    'Expose the native log normalizer directly, compare same-tensor masks, and test pressure as a signal against held-out task outcomes.',
    {'state':'What color is the clear daytime sky? Answer with one short color word.'})

async def run(ctx,opt):
    cases=[]
    for name,strings in [('Color words',['Blue','Red']),('Furniture words',['Chair','Table']),
                         ('One forced color',['Blue']),('Both vocabularies',['Blue','Red','Chair','Table'])]:
        body=pure_request(opt['state'],strings,12)
        scored=score_content(await ctx.call('Measure grammar pressure: '+name,body))
        if scored['text'] not in strings or scored['finish_reason']!='stop':
            raise ValueError('The grammar did not finish a complete allowed literal')
        rows=[];prefix=''
        for token in scored['tokens']:
            rows.append(dict(prefix=prefix,token=token,**pressure_from_token(token,body['strata_sampler'])))
            prefix+=token['token']
        cases.append(dict(name=name,grammar=body['grammar'],text=scored['text'],rows=rows))
    return dict(cases=cases,hypothetical=[dict(raw=[.594,.396,.01],q=[.6,.4,0]),dict(raw=[.006,.004,.99],q=[.6,.4,0])],
                semantics='Native cases use their own actual prefixes. Raw top-N is never summed as full grammar mass. Cross-request rows can differ slightly; no same-tensor comparison is implied.')
