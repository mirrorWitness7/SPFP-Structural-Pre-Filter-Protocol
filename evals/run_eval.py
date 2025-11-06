import json
from spfp.detector import detect

tp=fp=fn=0
for line in open("evals/cases.jsonl","r",encoding="utf-8"):
    case=json.loads(line)
    pred=set(detect(case["text"])["flags"])
    exp=set(case["expect"])
    tp+=len(pred&exp)
    fp+=len(pred-exp)
    fn+=len(exp-pred)
print({"precision": tp/max(tp+fp,1), "recall": tp/max(tp+fn,1),
       "tp":tp,"fp":fp,"fn":fn})
