import csv
import math
import numpy as np
from scipy.stats import pearsonr
from scipy.stats import spearmanr


# FILES RESULTS INITIALIZATION
csv_file_canons=open('../results/boxall-canons-stats.csv', 'w')
csv_file_tlangs=open("../results/boxall-canons-langs-total-stats.csv","w")
csv_file_plangs=open("../results/boxall-canons-langs-percentage-stats.csv","w")
csv_file_tcountries=open("../results/boxall-canons-countries-total-stats.csv","w")
csv_file_pcountries=open("../results/boxall-canons-countries-percentage-stats.csv","w")
csv_file_tconcordance=open("../results/boxall-canons-tconcordance.csv","w")
csv_file_pconcordance=open("../results/boxall-canons-pconcordance.csv","w")
csv_file_wdtconcordance=open("../results/boxall-canons-wdtconcordance.csv","w")
csv_file_wdpconcordance=open("../results/boxall-canons-wdpconcordance.csv","w")
csv_file_gender=open("../results/boxall-canons-gender.csv","w")
csv_file_wdgender=open("../results/boxall-canons-wdgender.csv","w")
csv_file_centroids=open("../results/boxall-centroids-women-langs.csv","w")
csv_file_correlations=open("../results/boxall-correlations.csv","w")
csv_file_macrocanon=open("../results/boxall-macrocanon-detail.csv","w")
csv_file_self_curves=open("../results/self_curves.csv","w")

list_form={}
list_boxall_books={}
list_genre={}
list_lang={}
list_lang_norm={}
stats_authors={}
mapping_country={}
mapping_lang={}
stats_canon={}

# WRITE CANONS GENDER
def write_canons_gender(type,output_file):
    print("Edition\tTotal\tMale\t% Male\tFemale\t% Female\tOthers\t% Others\tAnonymous\t% Anonymous",file=output_file)
    if type=="all": fields=["total","books_tgender_male","books_tgender_female","books_tgender_other","books_tanon"]
    if type=="wikidata": fields=["wikidata_items","books_wdgender_male","books_wdgender_female","books_wdgender_other","books_wdanon"]
    for r in columns_canon+virtual_canon: 
        print(r,end="",file=output_file)
        for f in fields:
            if f in ["total","wikidata_items"]:
                print("\t",stats_canon[r][f],end="",file=output_file)
            else:
                print("\t",len(stats_canon[r][f]),end="",file=output_file)
                if type=="all": print("\t",round(len(stats_canon[r][f])/stats_canon[r]["total"]*100,2),end="",file=output_file)
                if type=="wikidata": print("\t",round(len(stats_canon[r][f])/stats_canon[r]["wikidata_items"]*100,2),end="",file=output_file)
        print("",file=output_file)
    output_file.close()


# WRITE CANONS CONCORDANCES
def write_canons_concordance(type,output_file):
    for c in columns_canon+virtual_canon:
        print("\t",c,sep="",end="",file=output_file)
    print("",file=output_file)
    for r in columns_canon+virtual_canon: 
        print(r,end="",file=output_file)
        for c in columns_canon+virtual_canon:
            if type=="total": print("\t",stats_canon[r]["total_concordance"][c],sep="",end="",file=output_file)
            if type=="percentage": print("\t",round(stats_canon[r]["total_concordance"][c]/stats_canon[r]["total"]*100,2),sep="",end="",file=output_file)
            if type=="wdtotal": print("\t",stats_canon[r]["wikidata_concordance"][c],sep="",end="",file=output_file)
            if type=="wdpercentage": print("\t",round(stats_canon[r]["wikidata_concordance"][c]/stats_canon[r]["wikidata_items"]*100,2),sep="",end="",file=output_file)
        print("",file=output_file)
    output_file.close()

# WRITE LANGUAGES FILES STATS
def write_language_file_stats(type,output_file):
    for l in ordered_langs_norm:
        print("\t",mapping_lang[l]["code"],sep="",end="",file=output_file)
    print("",file=output_file)
    for c in stats_canon:
        print(c,sep="",end="",file=output_file)
        for l in ordered_langs_norm:
            if l in stats_canon[c]["langs_norm"]:
                if type=="total": print("\t",stats_canon[c]["langs_norm"][l],sep="",end="",file=output_file)
                if type=="percentage": print("\t",round(stats_canon[c]["langs_norm"][l]/stats_canon[c]["wikidata_items"]*100,3),sep="",end="",file=output_file)
            else:
                print("\t",0,sep="",end="",file=output_file)
        print("",file=output_file)
    output_file.close()

# WRITE COUNTRIES FILES STATS
def write_country_file_stats(type,output_file):
    for l in ordered_countries_norm:
        print("\t",mapping_country[l]["label"],sep="",end="",file=output_file)
    print("",file=output_file)
    for c in stats_canon:
        print(c,sep="",end="",file=output_file)
        for l in ordered_countries_norm:
            if l in stats_canon[c]["country_norm"]:
                if type=="total": print("\t",stats_canon[c]["country_norm"][l],sep="",end="",file=output_file)
                if type=="percentage": print("\t",round(stats_canon[c]["country_norm"][l]/stats_canon[c]["wikidata_items"]*100,1),sep="",end="",file=output_file)
            else:
                print("\t",0,sep="",end="",file=output_file)
        print("",file=output_file)
    output_file.close()


# COMPLETE CANON STATS
def complete_canon_stats(cv):
    stats_canon[cv]["total"]+=1

    if reg["ID-TYPE"]=="item": # WIKIDATA ITEMS
        stats_canon[cv]["books"].append(reg["BOOK-ID"])
        stats_canon[cv]["wikidata_items"]+=1
        stats_canon[cv]["tnwikis"]+=math.log(1+int(reg["NWIKIS"]))
        stats_canon[cv]["tnprops"]+=math.log(1+int(reg["NPROPS"]))
        stats_canon[cv]["tnwords"]+=math.log(1+int(reg["NWORDS"]))
        stats_canon[cv]["snwikis"]+=int(reg["NWIKIS"])
        stats_canon[cv]["snprops"]+=int(reg["NPROPS"])
        stats_canon[cv]["snwords"]+=int(reg["NWORDS"])


        # LANGS
        added_langs=[]
        added_langs_norm=[]
        list_reg_langs=reg["BOOK-LANGUAGE-ID"].split("|")
        if len(list_reg_langs)>0:
            for l in list_reg_langs:
                if l not in stats_canon[cv]["langs"]: stats_canon[cv]["langs"][l]=0
                if mapping_lang[l]["id"]=="Q1860": stats_canon[cv]["books_eng"].append(reg["BOOK-ID"])
                if mapping_lang[l]["id"] not in stats_canon[cv]["langs_norm"]:
                    stats_canon[cv]["langs_norm"][mapping_lang[l]["id"]]=0
                    stats_canon[cv]["langs_norm_w3dr"][mapping_lang[l]["id"]]={}
                    stats_canon[cv]["langs_norm_w3dr"][mapping_lang[l]["id"]]["tnwikis"]=0
                    stats_canon[cv]["langs_norm_w3dr"][mapping_lang[l]["id"]]["tnprops"]=0
                    stats_canon[cv]["langs_norm_w3dr"][mapping_lang[l]["id"]]["tnwords"]=0

                if l not in added_langs:
                    stats_canon[cv]["langs"][l]+=1
                    added_langs.append(l)
                if mapping_lang[l]["id"] not in added_langs_norm:
                    stats_canon[cv]["langs_norm"][mapping_lang[l]["id"]]+=1
                    added_langs.append(mapping_lang[l]["id"])
                    if reg["ID-TYPE"]=="item":
                        stats_canon[cv]["langs_norm_w3dr"][mapping_lang[l]["id"]]["tnwikis"]+=math.log(1+int(reg["NWIKIS"]))
                        stats_canon[cv]["langs_norm_w3dr"][mapping_lang[l]["id"]]["tnprops"]+=math.log(1+int(reg["NPROPS"]))
                        stats_canon[cv]["langs_norm_w3dr"][mapping_lang[l]["id"]]["tnwords"]+=math.log(1+int(reg["NWORDS"]))


        # COUNTRY AUTHORS
        if reg["AUTHOR-WIKIDATA-ID"]!="": 
            list_authors=reg["AUTHOR-WIKIDATA-ID"].split("|")
        else:
            list_authors=reg["AUTHOR-ID"].split("|")
        if len(list_authors)>0:
            for l in list_authors:
                if l not in stats_canon[cv]["authors"]:
                    stats_canon[cv]["authors"].append(l)
                    if l!="**Anonymous**":
                        for lc in stats_authors[l]["country"]:
                            if lc not in stats_canon[cv]["country"]:
                                stats_canon[cv]["country"][lc]=0
                            stats_canon[cv]["country"][lc]+=1
                        for lc in stats_authors[l]["country_norm"]:
                            if lc not in stats_canon[cv]["country_norm"]:
                                stats_canon[cv]["country_norm"][lc]=0
                            stats_canon[cv]["country_norm"][lc]+=1
        
    if reg["ID-TYPE"]=="no-item": stats_canon[cv]["no_wikidata_items"]+=1
    if reg["ID-TYPE"]=="Other-Author-Work" : stats_canon[cv]["oaw_wikidata_items"]+=1


    # GENDER AND ANONYMOUS AUTHOR STATS
    if reg["AUTHOR-WIKIDATA-ID"]!="": 
        list_authors=reg["AUTHOR-WIKIDATA-ID"].split("|")
    else:
        list_authors=reg["AUTHOR-ID"].split("|")
    if len(list_authors)>0:
        for l in list_authors:
            if l!="**Anonymous**":
                gender=stats_authors[l]["gender"]
                if gender not in ["male","female"]: gender="other"
                stats_canon[cv]["books_tgender_"+gender].append(reg["BOOK-ID"])
                if reg["ID-TYPE"]=="item":
                    stats_canon[cv]["books_wdgender_"+gender].append(reg["BOOK-ID"])
                    stats_canon[cv]["tnwikis_"+gender]+=math.log(1+int(reg["NWIKIS"]))
                    stats_canon[cv]["tnprops_"+gender]+=math.log(1+int(reg["NPROPS"]))
                    stats_canon[cv]["tnwords_"+gender]+=math.log(1+int(reg["NWORDS"]))
                    stats_canon[cv]["snwikis_"+gender]+=int(reg["NWIKIS"])
                    stats_canon[cv]["snprops_"+gender]+=int(reg["NPROPS"])
                    stats_canon[cv]["snwords_"+gender]+=int(reg["NWORDS"])
            else:
                stats_canon[cv]["books_tanon"].append(reg["BOOK-ID"])
                if reg["ID-TYPE"]=="item":
                    stats_canon[cv]["books_wdanon"].append(reg["BOOK-ID"])
                    stats_canon[cv]["tnwikis_anom"]+=math.log(1+int(reg["NWIKIS"]))
                    stats_canon[cv]["tnprops_anom"]+=math.log(1+int(reg["NPROPS"]))
                    stats_canon[cv]["tnwords_anom"]+=math.log(1+int(reg["NWORDS"]))
                    stats_canon[cv]["snwikis_anom"]+=int(reg["NWIKIS"])
                    stats_canon[cv]["snprops_anom"]+=int(reg["NPROPS"])
                    stats_canon[cv]["snwords_anom"]+=int(reg["NWORDS"])

    else:
        stats_canon[cv]["books_tgender_none"].append(reg["BOOK-ID"])
        if reg["ID-TYPE"]=="item": stats_canon[cv]["books_wdgender_none"].append(reg["BOOK-ID"])


# CANONS EDITIONS AND AGGREGATIONS INITIALIZATION
columns_canon=["NL","NO","HU","RU","RO","DK","PL","KO","JP","ES","IT","FR","DE","CZ","PT","ZH","EN-2006","EN-2008","EN-2010","EN-2012","EN-2018"]
virtual_canon=["ALL-EN","ANY-EN","NOT-EN","ONLY-NOT-EN","ONLY-EN","MICROCANON","MACROCANON"]
for c in columns_canon+virtual_canon: 
    stats_canon[c]={"books":[],"books_eng":[],"total":0,"wikidata_items":0,"no_wikidata_items":0,"oaw_wikidata_items":0,"langs":{},"langs_norm":{},"country":{},"country_norm":{},"authors":[],"langs_norm_w3dr":{},
    "books_tgender_male":[],"books_tgender_female":[],"books_tgender_other":[],"books_tgender_none":[],"books_tanon":[],
    "books_wdgender_male":[],"books_wdgender_female":[],"books_wdgender_other":[],"books_wdgender_none":[],"books_wdanon":[],
    "total_concordance":{},"wikidata_concordance":{},"tnwikis":0,"tnprops":0,"tnwords":0,"snwikis":0,"snprops":0,"snwords":0,
    "tnwikis_female":0,"tnprops_female":0,"tnwords_female":0,"snwikis_female":0,"snprops_female":0,"snwords_female":0,
    "tnwikis_male":0,"tnprops_male":0,"tnwords_male":0,"snwikis_male":0,"snprops_male":0,"snwords_male":0,
    "tnwikis_other":0,"tnprops_other":0,"tnwords_other":0,"snwikis_other":0,"snprops_other":0,"snwords_other":0,
    "tnwikis_anom":0,"tnprops_anom":0,"tnwords_anom":0,"snwikis_anom":0,"snprops_anom":0,"snwords_anom":0}
    for co in columns_canon+virtual_canon:
        stats_canon[c]["total_concordance"][co]=0
        stats_canon[c]["wikidata_concordance"][co]=0


# LOAD LANG NORMALIZATION
with open("../data/nor-books-langs.csv",encoding="utf-8-sig") as data:
    for reg in csv.DictReader(data,delimiter="\t"):
        mapping_lang[reg["LANGUAGE-ID"]]={}

        if reg["NOR-LANG-ID"]!="":
            mapping_lang[reg["LANGUAGE-ID"]]={"id":reg["NOR-LANG-ID"],"label":reg["LANGUAGE-LABEL"],"code":reg["CODE"]}
        else:
            mapping_lang[reg["LANGUAGE-ID"]]={"id":reg["LANGUAGE-ID"],"label":reg["LANGUAGE-LABEL"],"code":reg["CODE"]}

# LOAD COUNTRY NORMALIZATION
with open("../data/nor-country-authors.csv",encoding="utf-8-sig") as data:
    for reg in csv.DictReader(data,delimiter=","):
        mapping_country[reg["COUNTRY-ID"]]={}
        if reg["NOR-COUNTRY-AUTH-ID"]!="":
            mapping_country[reg["COUNTRY-ID"]]={"id":reg["NOR-COUNTRY-AUTH-ID"],"label":reg["COUNTRY-LABEL"]}
        else:
            mapping_country[reg["COUNTRY-ID"]]={"id":reg["COUNTRY-ID"],"label":reg["COUNTRY-LABEL"]}

# LOAD AUTHORS DATA
with open("../data/boxall-authors-full.csv",encoding="utf-8-sig") as data:
    for reg in csv.DictReader(data,delimiter="\t"):
        stats_authors[reg["AUTHOR-WIKIDATA-ID"]]={"label":reg["AUTHOR-WIKIDATA-LABEL"],"tbooks":[],"wdbooks":[],"gender":reg["AUTHOR-GENDER"],"country":[],"country_norm":[]}
        for l in reg["AUTHOR-COUNTRY"].split("|"):
            stats_authors[reg["AUTHOR-WIKIDATA-ID"]]["country"].append(l)
            if mapping_country[l]["id"] not in stats_authors[reg["AUTHOR-WIKIDATA-ID"]]["country_norm"]:
                stats_authors[reg["AUTHOR-WIKIDATA-ID"]]["country_norm"].append(mapping_country[l]["id"])
    stats_authors["**Anonymous**"]={"label":"Anonymous","tbooks":[],"wdbooks":[],"gender":"Unknwon","country":[],"country_norm":[]}

# CANONS AND AGGREGATION LIST CONSTRUCTION
with open("../data/boxall-books-full.csv",encoding="utf-8-sig") as data:
    for reg in csv.DictReader(data,delimiter="\t"):
        nwikis=0
        nprops=0
        nwords=0
        if reg["NWIKIS"]!="": nwikis=int(reg["NWIKIS"])
        if reg["NPROPS"]!="": nprops=int(reg["NPROPS"])
        if reg["NWORDS"]!="": nwords=int(reg["NWORDS"])

        list_boxall_books[reg["BOOK-ID"]]={"ID-TYPE":reg["ID-TYPE"],"TITLE-EN":reg["BOOK-WIKIDATA-LABEL-EN"],"TITLE-ES":reg["BOOK-WIKIDATA-LABEL-ES"],"NWIKIS":nwikis,"NPROPS":math.log(1+nprops),"NWORDS":math.log(1+nwords)}
    

        if reg["AUTHOR-WIKIDATA-ID"]!="": 
            list_authors=reg["AUTHOR-WIKIDATA-ID"].split("|")
        else:
            list_authors=reg["AUTHOR-ID"].split("|")
        if len(list_authors)>0:
            for author in list_authors:
                stats_authors[author]["tbooks"].append(reg["BOOK-ID"])
                if reg["ID-TYPE"]=="item":
                    stats_authors[author]["wdbooks"].append(reg["BOOK-ID"])

        is_virtual={"ALL-EN":True,"ANY-EN":False,"NOT-EN":False,"ONLY-NOT-EN":True,"ONLY-EN":True,"MICROCANON":True,"MACROCANON":True}
        for c in columns_canon:
            if reg[c]=="y":

                for co in columns_canon:
                    if reg[co]=="y":
                        stats_canon[c]["total_concordance"][co]+=1
                        if reg["ID-TYPE"]=="item":
                            stats_canon[c]["wikidata_concordance"][co]+=1
                complete_canon_stats(c)

            # WORKS THAT APPEAR IN ALL ENGLISH CANONS
            if c in ["EN-2006","EN-2008","EN-2010","EN-2012","EN-2018"] and reg[c]!="y": is_virtual["ALL-EN"]=False
            # WORKS THAT APPEAR IN ALL NON-ENGLISH CANONS
            if c not in ["EN-2006","EN-2008","EN-2010","EN-2012","EN-2018"] and reg[c]=="y": is_virtual["NOT-EN"]=True
            # WORKS THAT APPEAR ONLY IN ANY ENGLISH CANONS
            if c not in ["EN-2006","EN-2008","EN-2010","EN-2012","EN-2018"] and reg[c]=="y": is_virtual["ONLY-EN"]=False
            # WORKS THAT APPEAR ONLY IN ANY NON-ENGLISH CANONS
            if c in ["EN-2006","EN-2008","EN-2010","EN-2012","EN-2018"] and reg[c]=="y":
                is_virtual["ONLY-NOT-EN"]=False
                is_virtual["ANY-EN"]=True
            # WORKS THAT APPEAR IN ALL CANONS
            if reg[c]!="y": is_virtual["MICROCANON"]=False

        for c in columns_canon:
            if reg[c]=="y":
                for i in is_virtual:
                    if is_virtual[i]:
                        stats_canon[c]["total_concordance"][i]+=1
                        stats_canon[i]["total_concordance"][c]+=1
                        if reg["ID-TYPE"]=="item":
                            stats_canon[c]["wikidata_concordance"][i]+=1
                            stats_canon[i]["wikidata_concordance"][c]+=1

        for v in is_virtual:
            if is_virtual[v]:
                complete_canon_stats(v)


        for i in is_virtual:
            if is_virtual[i]:
                stats_canon[i]["total_concordance"][i]+=1
                if reg["ID-TYPE"]=="item":
                    stats_canon[i]["wikidata_concordance"][i]+=1


# CALCULATE SELF CANON CENTROID
def self_centroid(list,ntop):
    c=0
    nwikis=0
    nprops=0
    nwords=0
    for book in list:
        c+=1
        nwikis+=math.log(1+list[book]["nwikis"])
        nprops+=math.log(1+list[book]["nprops"])
        nwords+=math.log(1+list[book]["nwords"])
        if c==ntop: break
    result=math.sqrt(pow(nwikis/ntop,2)+pow(nprops/ntop,2)+pow(nwords/ntop,2))
    return(result)



# LOAD SELF CANON AND CALCULATE CURVE
list_self={}
curve_self_macrocanon=[]
curve_self_microcanon=[]

with open("../data/self-books-data-w3dr.csv",encoding="utf-8-sig") as data:
    for reg in csv.DictReader(data,delimiter="\t"):
        item=reg["BOOK-ID"]
        list_self[item]={}
        list_self[item]["nwikis"]=nwikis=int(reg["NWIKIS"])
        list_self[item]["nprops"]=nprops=int(reg["NPROPS"])
        list_self[item]["nwords"]=nwords=int(reg["NWORDS"])
        list_self[item]["wiki3drank"]=math.sqrt(pow(math.log(1+nwikis),2)+pow(math.log(1+nprops),2)+pow(math.log(1+nwords),2))

ordered_self=dict(sorted(list_self.items(),key=lambda item: item[1] ["wiki3drank"],reverse=True))

n_macrocanon=len(stats_canon["MACROCANON"]["books"])
n_microcanon=len(stats_canon["MICROCANON"]["books"])
c_macrocanon=0
c_microcanon=0
c_total=0
count=0
print("X\tP_MACROCANON\tP_MICROCANON",file=csv_file_self_curves)
for book in list_self:
    c_total+=1
    if book in stats_canon["MACROCANON"]["books"]: c_macrocanon+=1
    if book in stats_canon["MICROCANON"]["books"]: c_microcanon+=1
    p_macrocanon=c_macrocanon/n_macrocanon
    p_microcanon=c_microcanon/n_microcanon
    curve_self_macrocanon.append(p_macrocanon)
    curve_self_microcanon.append(p_microcanon)
    count+=1
    if count==1: print(c_total,p_macrocanon,p_microcanon,sep="\t",file=csv_file_self_curves)
    if count>99: count=0
print(c_total,p_macrocanon,p_microcanon,sep="\t",file=csv_file_self_curves)


# LOAD ZSCHIRNT CANON AND CALCULATE CENTROID
list_zschirnt={}
zschirnt_canon_centroid={"tnwikis":0,"tnprops":0,"tnwords":0,"wiki3drank":0}
n=0
with open("../data/zschirnt-books-data-w3dr.csv",encoding="utf-8-sig") as data:
    for reg in csv.DictReader(data,delimiter="\t"):
        item=reg["BOOK-ID"]
        if item!="":
            n+=1
            list_zschirnt[item]={}
            list_zschirnt[item]["nwikis"]=nwikis=int(reg["NWIKIS"])
            list_zschirnt[item]["nprops"]=nprops=int(reg["NPROPS"])
            list_zschirnt[item]["nwords"]=nwords=int(reg["NWORDS"])
            list_zschirnt[item]["wiki3drank"]=math.sqrt(pow(math.log(1+nwikis),2)+pow(math.log(1+nprops),2)+pow(math.log(1+nwords),2))
n_macrocanon=0
n_microcanon=0
for book in list_zschirnt:
    zschirnt_canon_centroid["tnwikis"]+=list_zschirnt[book]["nwikis"]
    zschirnt_canon_centroid["tnprops"]+=list_zschirnt[book]["nprops"]
    zschirnt_canon_centroid["tnwords"]+=list_zschirnt[book]["nwords"]
    if book in stats_canon["MACROCANON"]["books"]: n_macrocanon+=1
    if book in stats_canon["MICROCANON"]["books"]: n_microcanon+=1
zschirnt_canon_centroid["wiki3drank"]=math.sqrt(pow(math.log(1+zschirnt_canon_centroid["tnwikis"]/n),2)+pow(math.log(1+zschirnt_canon_centroid["tnprops"]/n),2)+pow(math.log(1+zschirnt_canon_centroid["tnwords"]/n),2))

print("--------------------------------------------------------")
print("SELF CENTROID 1001:",self_centroid(list_self,1001))
print("SELF CENTROID MACROCANON:",self_centroid(list_self,len(stats_canon["MACROCANON"]["books"])))
print("SELF CENTROID MICROCANON:",self_centroid(list_self,len(stats_canon["MICROCANON"]["books"])))
print("SELF-MACROCANON PERCENTAGE CONCORDANCE",100*curve_self_macrocanon[len(stats_canon["MACROCANON"]["books"])-1])
print("SELF-MICROCANON PERCENTAGE CONCORDANCE",100*curve_self_microcanon[len(stats_canon["MICROCANON"]["books"])-1])
print("--------------------------------------------------------")
print("ZSCHIRNT CANON SIZE:",len(list_zschirnt))
print("ZSCHIRNT PERCENTAGE PRESENCE IN BOXALL MACROCANON:",n_macrocanon/len(list_zschirnt)*100)
print("ZSCHIRNT PERCENTAGE PRESENCE IN BOXALL MICROCANON:",n_microcanon/len(list_zschirnt)*100)
print("ZSCHIRNT CENTROID:",zschirnt_canon_centroid["wiki3drank"])
print("--------------------------------------------------------")
print("Writing canon stats data...")
print("Edition\tTotal\tWikidata items\tNOT-Wikidata items\tOAW-Wikidata items\t% Wikidata items",file=csv_file_canons)
for c in stats_canon:
    print(c,stats_canon[c]["total"],stats_canon[c]["wikidata_items"],stats_canon[c]["no_wikidata_items"]+stats_canon[c]["oaw_wikidata_items"],stats_canon[c]["oaw_wikidata_items"],
          round(stats_canon[c]["wikidata_items"]/stats_canon[c]["total"]*100,2),sep="\t",file=csv_file_canons)

ordered_langs=dict(sorted(stats_canon["MACROCANON"]["langs"].items(), key=lambda item: item[1], reverse=True))
ordered_langs_norm=dict(sorted(stats_canon["MACROCANON"]["langs_norm"].items(), key=lambda item: item[1], reverse=True))
ordered_countries=dict(sorted(stats_canon["MACROCANON"]["country"].items(), key=lambda item: item[1], reverse=True))
ordered_countries_norm=dict(sorted(stats_canon["MACROCANON"]["country_norm"].items(), key=lambda item: item[1], reverse=True))

print("Writing normalized language canon stats data totals...")
write_language_file_stats("total",csv_file_tlangs)

print("Writing normalized language canon stats data percentage...")
write_language_file_stats("percentage",csv_file_plangs)

print("Writing normalized countries canon stats data totals...")
write_country_file_stats("total",csv_file_tcountries)

print("Writing normalized countries canon stats data percentage...")
write_country_file_stats("percentage",csv_file_pcountries)

print("Writing total canons concordance...")
write_canons_concordance("total",csv_file_tconcordance)

print("Writing percentage canons concordance...")
write_canons_concordance("percentage",csv_file_pconcordance)

print("Writing wikidata total canons concordance...")
write_canons_concordance("wdtotal",csv_file_wdtconcordance)

print("Writing wikidata percentage canons concordance...")
write_canons_concordance("wdpercentage",csv_file_wdpconcordance)

print("Writing all gender canons stats...")
write_canons_gender("all",csv_file_gender)

print("Writing Wikidata gender canons stats...")
write_canons_gender("wikidata",csv_file_wdgender)




sum_concordance=0
sum_books=0
l_values=[]

for r in columns_canon:
    for c in columns_canon:
        if c!=r:
            sum_concordance+=stats_canon[r]["wikidata_concordance"][c]
            sum_books+=stats_canon[r]["wikidata_items"]
            l_values.append(round(stats_canon[r]["wikidata_concordance"][c]/stats_canon[r]["wikidata_items"]*100,2))




print("Average percentage variability:",round(sum_concordance/sum_books*100,2))
a=np.array(l_values)
print(np.percentile(a,[25,50,75]))


# print(stats_authors["**Anonymous**"])

grouped_author_stats={}
for i in range(20,0,-1):
    grouped_author_stats[i]=0


for a in dict(sorted(stats_authors.items(), key=lambda item: len(item[1]["tbooks"]), reverse=True)):
    if a!="**Anonymous**": grouped_author_stats[len(stats_authors[a]["tbooks"])]+=1
    # print(stats_authors[a]["label"],len(stats_authors[a]["tbooks"]),stats_authors[a]["country_norm"],sep="\t")


var={}
var["cg"]=[]
var["cf"]=[]
var["ce"]=[]
var["cne"]=[]
var["co"]=[]
var["cno"]=[]
var["pf"]=[]
var["pe"]=[]
var["pne"]=[]
var["po"]=[]
var["pno"]=[]
relevant_langs=['Q1860','Q150','Q1321','Q188','Q652','Q7737','Q5146']
print("CANON\tTNWIKIS\tTNPROPS\tTNWORDS\tWiki3DRank centroid\tWiki3DRank centroid female\tPercentage female books\tWiki3DRank centroid relevant langs\tWiki3DRank centroid non relevant langs\tPercentage books relevant langs\tPercentage books non relevant langs\tWiki3DRank centroid english lang\tWiki3DRank centroid no english langs\tPercentage books in english lang\tPercentage books in non english langs",file=csv_file_centroids)
for c in columns_canon+virtual_canon:
    total_relevant=0
    total_non_relevant=0
    nwikis_relevant=0
    nprops_relevant=0
    nwords_relevant=0
    nwikis_non_relevant=0
    nprops_non_relevant=0
    nwords_non_relevant=0
    total_english=0
    total_non_english=0
    nwikis_english=0
    nprops_english=0
    nwords_english=0
    nwikis_non_english=0
    nprops_non_english=0
    nwords_non_english=0

    for l in stats_canon[c]["langs_norm"]:
        if l in relevant_langs:
            total_relevant+=stats_canon[c]["langs_norm"][l]
            nwikis_relevant+=stats_canon[c]["langs_norm_w3dr"][l]["tnwikis"]
            nprops_relevant+=stats_canon[c]["langs_norm_w3dr"][l]["tnprops"]
            nwords_relevant+=stats_canon[c]["langs_norm_w3dr"][l]["tnwords"]
        else:
            total_non_relevant+=stats_canon[c]["langs_norm"][l]
            nwikis_non_relevant+=stats_canon[c]["langs_norm_w3dr"][l]["tnwikis"]
            nprops_non_relevant+=stats_canon[c]["langs_norm_w3dr"][l]["tnprops"]
            nwords_non_relevant+=stats_canon[c]["langs_norm_w3dr"][l]["tnwords"]
        if l in ["Q1860"]:
            total_english+=stats_canon[c]["langs_norm"][l]
            nwikis_english+=stats_canon[c]["langs_norm_w3dr"][l]["tnwikis"]
            nprops_english+=stats_canon[c]["langs_norm_w3dr"][l]["tnprops"]
            nwords_english+=stats_canon[c]["langs_norm_w3dr"][l]["tnwords"]
        else:
            total_non_english+=stats_canon[c]["langs_norm"][l]
            nwikis_non_english+=stats_canon[c]["langs_norm_w3dr"][l]["tnwikis"]
            nprops_non_english+=stats_canon[c]["langs_norm_w3dr"][l]["tnprops"]
            nwords_non_english+=stats_canon[c]["langs_norm_w3dr"][l]["tnwords"]         

    total_wd_books=stats_canon[c]["wikidata_items"]
    total_wd_female=len(stats_canon[c]["books_wdgender_female"])
    total_wd_en=stats_canon[c]["langs_norm"]["Q1860"]
    wiki3drank_centroid=round(math.sqrt(pow(stats_canon[c]["tnwikis"]/total_wd_books,2)+pow(stats_canon[c]["tnprops"]/total_wd_books,2)+pow(stats_canon[c]["tnwords"]/total_wd_books,2)),6)
    wiki3drank_centroid_female=round(math.sqrt(pow(stats_canon[c]["tnwikis_female"]/total_wd_female,2)+pow(stats_canon[c]["tnprops_female"]/total_wd_female,2)+pow(stats_canon[c]["tnwords_female"]/total_wd_female,2)),6)
    wiki3drank_centroid_relevant=round(math.sqrt(pow(nwikis_relevant/total_relevant,2)+pow(nprops_relevant/total_relevant,2)+pow(nwords_relevant/total_relevant,2)),6)
    if total_non_relevant>0:
        wiki3drank_centroid_non_relevant=round(math.sqrt(pow(nwikis_non_relevant/total_non_relevant,2)+pow(nprops_non_relevant/total_non_relevant,2)+pow(nwords_non_relevant/total_non_relevant,2)),6)
    else:
        wiki3drank_centroid_non_relevant=0

    wiki3drank_centroid_english=round(math.sqrt(pow(nwikis_english/total_english,2)+pow(nprops_english/total_english,2)+pow(nwords_english/total_english,2)),6)
    if total_non_english>0:
        wiki3drank_centroid_non_english=round(math.sqrt(pow(nwikis_non_english/total_non_english,2)+pow(nprops_non_english/total_non_english,2)+pow(nwords_non_english/total_non_english,2)),6)
    else:
        wiki3drank_centroid_non_english=0

    if c in columns_canon:
        var["cg"].append(wiki3drank_centroid)
        var["cf"].append(wiki3drank_centroid_female)
        var["ce"].append(wiki3drank_centroid_english)
        var["cne"].append(wiki3drank_centroid_non_english)
        var["co"].append(wiki3drank_centroid_relevant)
        var["cno"].append(wiki3drank_centroid_non_relevant)
        var["pf"].append(total_wd_female/total_wd_books*100)
        var["pe"].append(total_english/total_wd_books*100)
        var["pne"].append(total_non_english/total_wd_books*100)
        var["po"].append(total_relevant/total_wd_books*100)
        var["pno"].append(total_non_relevant/total_wd_books*100)

    print(c,stats_canon[c]["tnwikis"],stats_canon[c]["tnprops"],stats_canon[c]["tnwords"],wiki3drank_centroid,wiki3drank_centroid_female,round(total_wd_female/total_wd_books*100,3),wiki3drank_centroid_relevant,wiki3drank_centroid_non_relevant,round(total_relevant/total_wd_books*100,3),round(total_non_relevant/total_wd_books*100,3),wiki3drank_centroid_english,wiki3drank_centroid_non_english,round(total_english/total_wd_books*100,3),round(total_non_english/total_wd_books*100,3),sep="\t",file=csv_file_centroids)


print("Writing centroid-percentage correlations data...")
for c in ["pf","pe","pne","po","pno"]:
    print("\t",c,sep="",end="",file=csv_file_correlations)
print("",file=csv_file_correlations)
for r in ["cg","cf","ce","cne","co","cno"]:
    print(r,end="",file=csv_file_correlations)
    for c in ["pf","pe","pne","po","pno"]:
        a=pearsonr(var[r],var[c])
        print("\t",round(a[0],3),sep="",end="",file=csv_file_correlations)
    print("",file=csv_file_correlations)


print("BOOK-ID\tTITLE-EN\tTITLE-ES\tNWIKIS\tNPROPS\tNWORDS\tCOLOR_GROUP\tCOLOR_FEMALE\tCOLOR_LANG",file=csv_file_macrocanon)

for b in list_boxall_books:
    book=list_boxall_books[b]
    if list_boxall_books[b]["ID-TYPE"]=="item":
        color1="#1694ee"
        color2="#1694ee"
        color3="#1694ee"
        if b in stats_canon["MICROCANON"]["books"]: color1="#ee4216"
        if b in stats_canon["ONLY-NOT-EN"]["books"]: color1="#d6c943"
        if b in stats_canon["MACROCANON"]["books_wdgender_female"]: color2="#c22681"
        if b in stats_canon["MACROCANON"]["books_eng"]: color3="#ee4216"

        print(b,book["TITLE-EN"],book["TITLE-ES"],book["NWIKIS"],book["NPROPS"],book["NWORDS"],color1,color2,color3,file=csv_file_macrocanon,sep="\t")


for k in grouped_author_stats:
    print(k,grouped_author_stats[k],sep="\t")
print("--------------------------------")

csv_file_centroids.close()
csv_file_canons.close()
csv_file_correlations.close()
csv_file_macrocanon.close()
csv_file_self_curves.close()




