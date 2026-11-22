#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""第 2 轮补充来源：为新增条目（名家、汉代诸子、玄学、禅宗、近代、西方名家）补可核验来源。"""
import json,os,ssl,re,time,urllib.parse,urllib.request
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); SRC=os.path.join(ROOT,"sources.json")
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Safari/537.36'}
CTX=ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
def fetch(u,tries=2,t=18):
    for i in range(tries):
        try:
            r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=t,context=CTX)
            return r.status,r.read().decode('utf-8','ignore')
        except Exception as e:
            c=getattr(e,'code',0) or 0
            if c in (403,429,503) and i==0: time.sleep(2.0); continue
            return c,""
    return 0,""
def meta(h,n):
    m=re.search(r'<meta\s+name="%s"\s+content="([^"]*)"'%re.escape(n),h,re.I)
    return re.sub(r'<[^>]+>','',m.group(1)).strip() if m else ""
SEP=["kripke","avicenna","pascal","seneca","epictetus","merleau-ponty","adorno","beauvoir",
     "austin-jl","anscombe","logic-modal","chinese-room","medieval-arabic","byzantine-philosophy",
     "wang-yangming","confucian-traditions","chinese-epistemology"]
IEP=["kripke","avicenna","pascal","seneca","epictetus","merleau-ponty","adorno","beauvoir","austin"]
WS=[("ws-qianfulun","《潜夫论》","王符",150,"东汉政论，三十六篇","https://zh.wikisource.org/wiki/"+urllib.parse.quote("潛夫論"),"潛夫論","东汉社会批判与政治思想"),
    ("ws-shenjian","《申鉴》","荀悦",200,"东汉末政论，五卷","https://zh.wikisource.org/wiki/"+urllib.parse.quote("申鑒"),"申鑒","“性三品”与政治论"),
    ("ws-chongyoulun","《崇有论》","裴頠",297,"西晋玄学崇有派代表作，见《晋书》卷三十五","https://zh.wikisource.org/wiki/"+urllib.parse.quote("晉書/卷035"),"崇有論","“无不能生有”的核心论证"),
    ("ws-gongsunlongzi","《公孙龙子》","公孙龙",-300,"六篇，名家仅存的系统著作","https://zh.wikisource.org/wiki/"+urllib.parse.quote("公孫龍子"),"公孫龍子","白马论、坚白论、指物论"),
    ("ws-qiusu","《訄书》","章太炎",1900,"初刊1900年，后修订为《检论》","https://zh.wikisource.org/wiki/"+urllib.parse.quote("訄書"),"訄書","章太炎的学术与政治论集")]
def main():
    d=json.load(open(SRC,encoding='utf-8')); have={s['id'] for s in d['sources']}; added=0
    def put(rec):
        nonlocal added
        if rec['id'] in have: return
        d['sources'].append(rec); have.add(rec['id']); added+=1
        print("%-4s %-34s %s"%(rec['verify']['http_status'],rec['id'],'verified' if rec['verified'] else 'FAILED'),flush=True)
    for s in SEP:
        u="https://plato.stanford.edu/entries/%s/"%s; c,h=fetch(u)
        ok=c==200 and "Stanford Encyclopedia" in h
        put({"id":"sep-"+s,"title":"%s（SEP 词条）"%(re.sub(r'<[^>]+>','',(re.search(r'<h1[^>]*>(.*?)</h1>',h,re.S).group(1) if ok and re.search(r'<h1[^>]*>(.*?)</h1>',h,re.S) else s)).strip()),
             "author":meta(h,"citation_author") or "Stanford Encyclopedia of Philosophy 编辑部",
             "year":int(meta(h,"citation_publication_date")[:4]) if re.match(r"\d{4}",meta(h,"citation_publication_date")) else None,
             "year_note":"首次发布年份见页面","publisher":"Stanford Encyclopedia of Philosophy（斯坦福大学）","type":"百科","url":u,"url2":None,
             "link_ok":True if ok else ("blocked" if c in (401,403,429) else False),"verified":bool(ok),
             "note":"同行评审的学术百科","unit_hint":"",
             "verify":{"method":"http-page+citation_meta","http_status":c,"checked_at":time.strftime("%Y-%m-%d"),"keyword":"Stanford Encyclopedia","keyword_seen":bool(ok)}})
        time.sleep(0.6)
    for s in IEP:
        u="https://iep.utm.edu/%s/"%s; c,h=fetch(u)
        ok=c==200 and "Internet Encyclopedia" in h
        put({"id":"iep-"+s,"title":"%s（IEP 词条）"%s,"author":"Internet Encyclopedia of Philosophy（作者见页面）","year":None,
             "year_note":"IEP 词条不固定标注出版年","publisher":"Internet Encyclopedia of Philosophy","type":"百科","url":u,"url2":None,
             "link_ok":True if ok else ("blocked" if c in (401,403,429) else False),"verified":bool(ok),"note":"与 SEP 互补的学术百科",
             "unit_hint":"","verify":{"method":"http-page","http_status":c,"checked_at":time.strftime("%Y-%m-%d"),"keyword":"Internet Encyclopedia","keyword_seen":bool(ok)}})
        time.sleep(0.6)
    for sid,title,author,year,note,url,kw,hint in WS:
        c,h=fetch(url); ok=c==200 and kw in h
        put({"id":sid,"title":title,"author":author,"year":year,"year_note":note,"publisher":"维基文库（Wikimedia Wikisource）",
             "type":"原典","url":url,"url2":None,"link_ok":True if ok else ("blocked" if c in (401,403,429) else False),
             "verified":bool(ok),"note":"公有领域全文；参校中华书局/上海古籍点校本","unit_hint":hint,
             "verify":{"method":"http-page","http_status":c,"checked_at":time.strftime("%Y-%m-%d"),"keyword":kw,"keyword_seen":bool(ok)}})
        time.sleep(0.6)
    order={"原典":0,"百科":1,"学术著作":2,"论文":3}
    d["sources"].sort(key=lambda r:(order.get(r["type"],9),r["id"]))
    for i,r in enumerate(d["sources"],1): r["n"]=i
    d["meta"]["total"]=len(d["sources"]); d["meta"]["verified"]=sum(1 for s in d["sources"] if s["verified"])
    d["meta"]["by_type"]={t:sum(1 for s in d["sources"] if s["type"]==t) for t in order}
    json.dump(d,open(SRC,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
    print("\n新增 %d；总计 %d，verified %d"%(added,d["meta"]["total"],d["meta"]["verified"]))
main()
