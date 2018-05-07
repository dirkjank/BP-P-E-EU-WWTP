
# coding: utf-8

# # BP-P-E EU WWTP MODEL
# ## SETUP

# In[1]:

# Import Required Packages
import networkx as nx
import math
import numpy as np
import pyproj
from itertools import groupby as g
from pyproj import Proj, transform
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib import gridspec


# In[2]:

#Load in node data files
P = nx.read_shp("C:\\Users\\Dirk-Jan\\Dropbox\\DJ\\Python\\EU_P_BP_E\\Nodes\\Plastics\\PlasticNodesEU_4326.shp")
U = nx.read_shp("C:\\Users\\Dirk-Jan\\Dropbox\\DJ\\Python\\EU_P_BP_E\\Nodes\\Urban\\UrbNodesEU_4326.shp")
A = nx.read_shp("C:\\Users\\Dirk-Jan\\Dropbox\\DJ\\Python\\EU_P_BP_E\\Nodes\\Agriculture\\AgricultureEU_4326.shp")
#import transportation network
NW = nx.read_shp("C:\\Users\\Dirk-Jan\\Dropbox\\DJ\\Python\\EU_P_BP_E\\Nodes\\Network\\NetworkEU_4326.shp")

#Create a dictionary for storing datafiles and for easy referencing
DDef = {}
DDef['Plastics'] = P
DDef['Agriculture'] = A

#Import or define other data
#TIMESPAN
first_year = 2007
final_year = 2015
yearsl = [i for i in range(first_year,final_year+1)]

#PRICE DATA
##Electricity
Elr = [10.65,11.26,11.51,11.54,11.72,11.88,12.13,12.52,12.65] #[cents/kwh] ##https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_3
El = [[E*0.9,E,E*1.1] for E in Elr] #generate range around data (+-10%)
##Fuel
Diesel = [8.14,11.26,6.42,8.31,11.41,11.79,11.42,10.62,6.30] #[$/L] ##https://www.indexmundi.com/commodities/?commodity=diesel&months=180
Bunker = [341.16,341.16,341.16,341.16,467.48,606.56, 686.00,632.44,614.81] #[$/t] ##https://www.worldscale.co.uk/bookpage/bunkerprices
CO = [91.63,103.66,84.93,102.26,118.55,109.53,100.79,96.19,81.30] #[$/L] Crude Oil
##DAP fertilizer
Ppricedata = [] #DAP prices 2007 to 2015 ##https://www.indexmundi.com/commodities/?commodity=dap-fertilizer
Ppricedata.append([267.6,345.38,420.5,432.38,426.38,434.5,436.25,429.4,431.88,451.3,521,594]) #2007
Ppricedata.append([707.7,828.13,1044.75,1200.63,1199.15,1175.00,1185.40,1176.88,1098.75,970,612.5,407.5]) #2008
Ppricedata.append([351,367.88,367.63,335.4,297.5,277.75,293.3,318.63,316.78,300.11,290.25,360.4]) #2009
Ppricedata.append([427.5,490.5,476.25,466,460.63,448,461.25,496.13,525,575,588,593.9]) #2010
Ppricedata.append([595.75,603.75,605.5,617.13,609.75,625,650.63,659.38,642.5,630.88,611.3,575]) #2011
Ppricedata.append([530,517.3,502.5,518.13,553,564.38,563.13,559,573,573,524.8,499]) #2012
Ppricedata.append([485,482.25,507.5,508.25,485.1,476.1,460,438.13,398.13,377.3,351.25,369.88]) #2013
Ppricedata.append([438.3,490.63,499.38,470.63,444.6,461.5,499.4,505,481.63,466.5,452.75,459.63]) #2014
Ppricedata.append([480.4,485.25,479,464,470,473,469,464,460,442,416,399.17]) #2015
##PP resin prices
BPpricedatar = [] #PP prices ##http://www.plasticsnews.com/resin/commodity-thermoplastics/historical-pricing?grade=1310705|Vol1
BPpricedatar.append([95.5,89.5,86.5,85.5,81.5,77.5,72.5])
BPpricedatar.append([66.5,96.5,107.5,121.5,110.5,103.5,99.5,93.5])
BPpricedatar.append([87.5,84.5,94.5,82.5,78.5,77.5,68.5,65.5,59.5,56.5])
BPpricedatar.append([96.5,98.5,95.5,93.5,101.5,113.5,106.5,101.5,94.5,91.5])
BPpricedatar.append([97.5,103.5,117.5,121.5,136.5,126.5,111.5,116.5,99.5])
BPpricedatar.append([98.5,97.5,93.5,91.5,91.5,90.5,92.5,107.5,117.5,112.5,95.5])
BPpricedatar.append([107.5,108.5,110.5,105.5,102.5,103.5,113.5,119.5,113.5])
BPpricedatar.append([113.5,118.5,114.5,109.5,112.5,113.5,114.5,115.5,116.5,111.5])
BPpricedatar.append([90.5,88.5,85.5,86.5,88.5,89.5,88.5,89.5,93.5,94.5,93.5,103.5])
BPpricedata = [[i*22.05 for i in k] for k in BPpricedatar] #from cents per pound to dollars per tonne

#QUANTITY DATA
##Population growth
popr = [498300775,500297033,502090235,503170618,502964837,504041384,505143171,506973868,508504320,510278701] #http://ec.europa.eu/eurostat/web/population-demography-migration-projections/population-data/database
pop = [round(i/popr[4],3) for i in popr] #Node data for 2011 (4th simulation year), so determine conversion coefficient for other years.
##Polypropylene (PP) demand Europe
PPdem = [9.4,8.7,8.5,8.8,8.9,8.6,8.6,8.7,9.2,9.6] #[Mt] ##http://www.plasticseurope.org/en/resources/publications
TotPPdem= sum([P.node[n]['PlasStar'] for n in P.nodes()])
##Agricultural expansion
AEr = [106.15,110.40,111.74,114.36,117.83,119.20,123.33,124.18,125] #https://data.worldbank.org/topic/agriculture-and-rural-development
AE = [i/AEr[0] for i in AEr]


# In[3]:

#PARAMETERS
##WWTP
sp= 16/1000 #Sludge Production [t d.s./a/PE]
SHc = 160   #[$/tonne d.s.] Sludge handling costs ##https://cgi.tu-harburg.de/~awwweb/wbt/emwater/documents/lesson_c2.pdf
CODpp = 100*365/1000000 #[t/PE/a] #from 100 g/per person/day Chemical Oxygen Demand
TSpp= 70*365/1000000 #[t/PE/a] #from 70 g/per person/day Total Solids
VSpp= TSpp*0.7 #70% of total solids are volatile
TPpp = 0.77/1000 #[t/a] phosphorus discharge to wastewater per annum
##Tech
PBT = 15   #[a] payback time
##Phosphorus
dpS = 0.14  #P concentration struvite
MgCl = 250  #Price magnesium chloride       
Pm = MgCl/(24/92)*0.77       # Cost per ton of Pm. 0.77 tons of magnesium required per ton phosphorus (1:1 molar removal ratio; 24 g/mol Mg, 31 g/mol P)# Price magnesium chloride per ton (250) [$/ton] OSTARA, 34% Mg by mass
savingsP = 0.89*1000/0.14      # (0.89*1000/0.14) savings of struvite precipitation per tonne of P produced due to less scaling and handling (Shu et al)        
CMUP = round(Pm,3)
REP = 0.2 #[-] recovery efficienyof influent
###Big installation cost
WWIUPb = 180000 # [$] (Wastewater Treatment Urban investment Costs + annual costs - resource costs)  #Egle paper
PEPb = 500000 # PE serviced
###Small installation
WWIUPs = 120000 # [$] (Wastewater Treatment Urban investment Costs + annual costs - resource costs)  #Egle paper
PEPs = 100000 # PE serviced

##Biopolymers
dpBP =1    #PHB concentration
ChemCost = 0.41*1000 #[$/tPHB]
savingsBP = 0.6*1000 #[$/tPHB]
CMUBP = ChemCost-savingsBP
WWIUBP = 1800000    #Yearly investment in Equipment/Material Cost (over 15 years)
PEBP = 100000          #people serviced per installation (Population Equivalents)
Rec = 16/1000
###Physio-chemical
####Fermentation Process
AcidConv= 0.91 #[g COD/gCOD COD] Acidification conversion capacity
SelYield = 0.34 #[g XX/g COD]
AccuYield = 0.44 #[g PHA/g COD] Accumulation yield
####Down Stream Process


# In[4]:

#Calculate distances between WWTP and consumers
from math import sin, cos, sqrt, atan2, radians
import networkx as nx
R = 6373.0
dist = {} 
for u in U.nodes(): #WWTPs
    lat1 = radians(u[0])
    lon1 = radians(u[1])
    for i in DDef.values(): #Demand nodes
        for n in i.nodes():
            lat2 = radians(n[0])
            lon2 = radians(n[1])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            dist[(u,n)]= R * c
TcWl = [] #Yearly water transport cost constant
TcLl = [] #Yearly land transport cost constant
for idx in range(0,len(yearsl)): #Calculate for each simulation year.        
    #Truck
    Pd = Diesel[idx]    #Price of diesel [$/Litre]
    El = 0.016           #[l/km/t] https://www.energy.gov/sites/prod/files/2014/03/f9/2005_deer_erkkila.pdf
    Wl = 60              #[t]
    Vl = 80              #[km/h]
    Lc = 20              #[$/h]
    Cfl = 0.5            #[$/km] http://www.rtsfinancial.com/guides/trucking-calculations-formulas
    emL = 0.53           #[kg/L] Co2 per liter diesel
    ##Ship
    Pb = Bunker[idx]       #[$/t]
    Ew = 60.9              #[t/d]
    Ww = 2777              #DWT[t]
    Vw = 924              #[km/d]   (https://www.insee.fr/en/statistiques/serie/001642883) June 2005
    Cfw = 9989             #[$/d] #daily fixed costs
    emW = 3130            #[kg/T] Co2 per tonne bunker
    ##Final Transport Costs    
    TcWl.append(((Pb*Ew+Cfw)/Vw)/Ww)
    TcLl.append(Pd*El+(Cfl+(Lc/Vl))/Wl)


# # Technology Specifications

# In[5]:

def E1recov(PBT,COD,TS,VS,TP,Sludge): # Pastor 2008
    HVM = 15.4  #[kwh/kgM] LHV calorific value of methane   ##https://www.engineeringtoolbox.com/fuels-higher-calorific-values-d_169.html
    VMM = 0.716 #[kg/m3] methane     
    BGP = 1.01 #±0.21 [l/gTVSrem][m3/kg]
    CH4p = 0.63 # ±1% of CH4 in biogas [%]
    
    Sludger = 0.7 #reduction in output sludge (???)
    VSr = 0.59  #removal of volatile solids
    CODr = 0.66 #removal of COD
    TSr = 0.43 #removal of total solids
    TPr = 0.23 #removal of total phosphorus
    kwP2 = round(BGP*CH4p*VMM*VS*VSr*HVM) #(kwh/a) Pastor 2008, #https://www.engineeringtoolbox.com/fuels-higher-calorific-values-d_169.html

    ##Tech 1: Reciprocating engines; Tech 2: gas turbines; Tech 3: Fuel Cells #https://www.sciencedirect.com/science/article/pii/S0378775313000402#bib6
    #https://www.cwwga.org/documentlibrary/121_EvaluationCHPTechnologiespreliminary[1].pdf
    ETech= [1,2,3,4]
    CRr = [[110,4400],[600,22000],[100,2800],[30,250]] #[kW] electrical output capacity (power)
    CR = [[round(CRr[n][i]*8760) for i in range(2)] for n in range(len(ETech))] #[kwh/a] electrical output capacity (power) per year
    ER = [[0.30,0.42],[0.19,0.34],[0.36,0.50],[0.26,0.30]] #[-] electrical conversion efficiency
    HER = [[0.35,0.49],[0.40,0.52],[0.30,0.40],[0.30,0.37]] #[-] heat recovery efficiency
    Omc = [[0.025,0.01],[0.01,0.008],[0.019,0.004],[0.012,0.025]] #[$/kwh] O&M costs
    OR = [[28000,90000],[30000,50000],[10000,80000],[30000,50000]] #[h] overhaul
    ECr = [[1600,465],[2000,1100],[5280,3800],[800,1600]] #[$/kw] equipment cost
    IC = [[ECr[n][i]*CRr[n][i] for i in range(2)] for n in range(len(ETech))]#[$] equipment cost
    CIR = [[round(CR[n][i]/(ER[n][i])) for i in range(2)] for n in range(len(ETech))]#[kwh/a] #input capacity derived from output power and efficiencies, working at 70% capacity

    ##Electricity2- Biogas #https://sswm.info/sites/default/files/reference_attachments/MES%202003%20Chapter%204.%20Methane%20production%20by%20anaerobic%20digestion%20of%20wastewater%20and%20solid%20wastes.pdf
    UNE = [] #List of recovery output for each generator type
    for i in range(len(ETech)): #for each generator tech
        if kwP2 < min(CIR[i]): #If gas production is out of range of generator capacity for that type
            UNE.append([0,0,ETech[i]])
        elif kwP2 in range(min(CIR[i]),max(CIR[i])): #If gas production is within range of generator capacity for that type
            Et = (kwP2-min(CIR[i]))/(max(CIR[i])-min(CIR[i])) #[-][0-1]scale of generator type
            Eto = 1-Et
            LS = (Et*(max(OR[i])-min(OR[i]))+min(OR[i]))/8760 #[a] Lifespan
            Crr = Et*(max(CRr[i])-min(CRr[i]))+min(CRr[i]) # output capacity
            ECC = Eto*(max(IC[i])-min(IC[i]))+min(IC[i]) #[$] Capital costs per kw output capacity (power)
            EomC = Eto*(max(Omc[i])-min(Omc[i]))+min(Omc[i]) #[$/kwh] O&M costs
            R = ((Et*(max(CR[i])-min(CR[i]))+min(CR[i]))) #[kwh] Energy recovered per annum
            HR = ((Et*(max(HER[i])-min(HER[i]))+min(HER[i])))*kwP2 #[kwh] Heat recovered per annum
            ERC = (ECC*Crr+EomC*R)/R #[$/kwh] energy recovery cost
            UNE.append([R,ERC,ETech[i]]) #Total recovery cost [$], energy recovered [kwh], recovery cost per kwh [$/kwh], generator type
        elif kwP2 > max(CIR[i]): #If gas production is greater than the highest capacity generator for that type
            BP = math.floor(kwP2/max(CIR[i])) #How many big generators
            kwP3 = (kwP2 - max(CIR[i])*BP) #residual to determine how many small installations 
            Crrb = BP*(max(CRr[i])) #total power
            ECCb = min(IC[i]) #[$] Capital costs per output capacity (power)
            EomCb = min(Omc[i]) #[$/kwh] O&M costs
            Rb = BP*max(CR[i]) #[kwh] Energy recovered per annum
            ERCb = (ECCb*Crrb+EomCb*Rb)/Rb #[$/kwh] energy recovery cost big installations
            if kwP3 in range(min(CIR[i]),max(CIR[i])):
                Ets = (kwP3-min(CIR[i]))/(max(CIR[i])-min(CIR[i])) #[-][0-1]scale
                Etso = 1-Ets
                Crrs = Ets*(max(CRr[i])-min(CRr[i]))+min(CRr[i])
                ECCs = Etso*(max(IC[i])-min(IC[i]))+min(IC[i]) #[$] Capital costs per year
                EomCs = Etso*(max(Omc[i])-min(Omc[i]))+min(Omc[i]) #[$/kwh] O&M costs
                Rs = ((Ets*(max(CR[i])-min(CR[i]))+min(CR[i]))) #[kwh] Energy recovered per annum
                ERCT = (ERCb+(ECCs*Crrs+EomCs*Rs)/Rs) #[$/kwh] energy recovery cost
                R=Rs+Rb
                UNE.append([R,ERCT,ETech[i]])
            elif kwP3 < min(CIR[i]):
                UNE.append([Rb,ERCb,ETech[i]])
    #Which generator type has lowest production cost.
    E1rec = [r[0] for r in UNE if r[0] == min([k[0] for k in UNE])][0]       
    E1RC = [r[1] for r in UNE if r[0] == min([k[0] for k in UNE])][0]
    E1T = [r[2] for r in UNE if r[0] == min([k[0] for k in UNE])][0]
    
    #Output wastewater composition after this recovery phase
    CODn=COD*CODr #PAstor 2008
    TSn=TS*(1-TSr)
    VSn=VS*(1-VSr)
    TPn=TP*(1-TPr)
    Sludgen = Sludge*(1-Sludger)
    return E1rec,E1RC,E1T,CODn,TSn,VSn,TPn,Sludgen


# In[6]:

def E2recov(PBT,COD,TS,VS,TP,Sludge): # Pastor 2008
    HV = 9000 #[kJ/kg] caloric value of sludge ##Stillwell (2010)
    HR = 10550 #[kJ/kwh] electrical conversion rate ##Stillwell (2010)
    MC = 0.7 #mover capacity - average power output of electric generator wrt total capacity output
    E2rec = round(sludge*HV/HR)
    E2RC = round(((0.0283*sludge+1.633*1000000/PBT))/E2rec,3) 
    Sludgen = 0
    TPn = 0
    VSn = 0
    TSn = 0
    CODn = 0
    E2T = 1
    return E2rec,E2RC,E2T,CODn,TSn,VSn,TPn,Sludgen


# In[7]:

def BPrecov(PBT,COD,TS,VS,TP,Sludge): #Fernandez-Dacosta 2015
    CODr = 0.3   #0.1
    TSr = 0.3
    VSr = 0.3
    TPr = 0.3
    Sludger =0.7
    
    AcidConv= 0.91 #[g COD/gCOD COD] Acidification conversion capacity
    #SelYield = 0.34 #[g XX/g COD]
    AccuYield = 0.44 #[g PHA/g COD] Accumulation yield
    Reff = 73.5 #Downstream Recovery efficiency #Fernandez-Dacosta 2015
    BPrec = COD*AcidConv*AccuYield*Reff#*SelYield
    BPRC = round(BPrec*ChemCost+WWIUBP/PBT,3)
    #Downstream proces
    ##missing
    
    CODn=COD*CODr #Pastor 2008
    TSn=TS*TSr
    VSn=VS*VSr
    TPn=TP*TPr
    Sludgen = Sludge*Sludger
    return(BPrec,BPRC,CODn,TSn,VSn,TPn,Sludgen)


# In[8]:

def Precov(BP,SP,TP,sludge):
    TPr = 0.2
    Prec = TP*TPr #total P recovery potential
    PRC = round((WWIUPb*BP+WWIUPs*SP+CMUP*Prec)/Prec,3)
    srP = 0.5 # sludge reduction ##file:///C:/Users/Dirk-Jan/Downloads/ubc_2004-0712.pdf
    sludge = sludge*(1-srP)
    return(Prec,PRC,sludge)


# # Model

# In[9]:

combinations = [['E1','P','E2'],['E1','P',],['E1'],['E1','E2'],
                ['BP','P','E2'],['BP','P'],['BP'],['BP','E2'],
                ['P','E2'],['E2'],['P'],['N']]


# In[10]:

#Determine Production costs for different combinations
Nodeprofitdict = {}
for idx,value in enumerate(yearsl): #For all simulation years
    profitnodes = {}
    for u in U.nodes(): #For all WW nodes
        prod = {}
        for idx2,comb in enumerate(combinations):
            popu = U.node[u]['DN']*pop[idx] #population serviced that year
            BP = math.floor(popu/PEPs) #big WWTP's in node vicinity
            SP =  math.ceil((popu-PEPb*BP)/PEPs) #small WWTP's in node vicinity
            
            #Total wastewater pollutant loads
            sludge = popu*sp #[t/a] sludge
            COD= popu*CODpp #[t/a] COD
            TS= popu*TSpp #[t/a] Total solids
            VS= popu*VSpp #[t/a] Volatile solids
            TP = popu*TPpp #[t/a] total phosphorus
        
            if 'E1' in comb:#Electricity1
                E1rec,E1RC,E1T,COD,TS,VS,TP,sludge = E1recov(PBT,COD,TS,VS,TP,sludge)
            else:
                E1rec = 0
                E1RC = 0
                E1T = -1
            if 'BP' in comb:
                BPrec,BPRC,COD,TS,VS,TP,sludge = BPrecov(PBT,COD,TS,VS,TP,sludge)
            else:
                BPrec = 0
                BPRC = 0
            if 'P' in comb:
                Prec,PRC,sludge = Precov(BP,SP,TP,sludge)
            else:
                Prec = 0
                PRC = 0
            if 'E2' in comb:#Electricity2           
                E2rec,E2RC,E2T,COD,TS,VS,TP,sludge = E2recov(PBT,COD,TS,VS,TP,sludge)
            else:
                E2rec = 0
                E2RC = 0
                E2T = -1
            prod[idx2] = ((E1rec,E1RC,E1T),(BPrec,BPRC),(Prec,PRC),(E2rec,E2RC,E2T))                  
        profitnodes[u] = prod.copy()
    Nodeprofitdict[yearsl[idx]] = profitnodes.copy()


# In[11]:

chk=1 #check only closest 1
yearsl2 = yearsl #incase you want to analyse only for one year (quicker)
Profityear = {}
for idx,yr in enumerate(yearsl):
    if yr in yearsl2:
        TcW = TcWl[idx]
        TcL = TcLl[idx]
        Profit = []
        for u in Nodeprofitdict[yr].keys():
            #Transportation Cost
            TRCP = {}
            TRCA = {}
            for p in P.nodes():
                D = dist[(u,p)]
                Fw = (85/(1+math.exp(-(D-500)/100)))/100 #[0-1]
                Fl = 1-Fw #[0-1]
                trc = D*(Fw*TcW+Fl*TcL)/dpBP
                TRCP[p] = trc
            for a in A.nodes():
                D = dist[(u,a)]
                Fw = (85/(1+math.exp(-(D-500)/100)))/100 #[0-1]
                Fl = 1-Fw #[0-1]
                trc = D*(Fw*TcW+Fl*TcL)/dpS
                TRCA[a] = trc
            
            #sort closest buyers
            TRCAsorted = sorted(TRCA.items(), key=lambda x:x[1], reverse=False)
            TRCPsorted = sorted(TRCP.items(), key=lambda x:x[1], reverse=False)
            for c,prodcost in Nodeprofitdict[yr][u].items():#prodcost[0] = E1, prodcost[1] = BP, prodcost[2] = P,, prodcost[3] = E2            
                comb = combinations[c]
                #[x][0] = recovery amounts, [x][1] = recovery cost 
                if 'P' in comb and 'BP' not in comb:   
                    for i in range(0,chk):
                        a = TRCAsorted[i][0]
                        p = 'none'
                        trc = TRCAsorted[i][1]
                        prof = (np.mean(Ppricedata[idx])-(prodcost[2][1]+trc))*prodcost[2][0]                        +(Elr[idx]-(prodcost[0][1]+prodcost[3][1]))*(prodcost[0][0]+prodcost[3][0])
                        inv = 'BAU'
                        Profit.append((prof,u,comb,inv,a,p))
                if 'BP' in comb and 'P' not in comb:
                    for i in range(0,chk):
                        p = TRCPsorted[i][0]
                        a = 'none'
                        trc = TRCPsorted[i][1]
                        prof = (np.mean(BPpricedata[idx])-(prodcost[1][1]+trc))*prodcost[1][0]                        +(Elr[idx]-(prodcost[0][1]+prodcost[3][1]))*(prodcost[0][0]+prodcost[3][0])
                        inv = 'BAU'
                        Profit.append((prof,u,comb,inv,a,p))
                if 'BP' in comb and 'P' in comb:
                    for i in range(0,chk):
                        p = TRCPsorted[i][0]
                        trcp = TRCPsorted[i][1]
                        for j in range(0,chk):     
                            a = TRCAsorted[j][0]
                            trca = TRCAsorted[j][1]
                            nosub = (np.mean(BPpricedata[idx])-(prodcost[1][1]+trcp))*prodcost[1][0]                                +(np.mean(Ppricedata[idx])-(prodcost[2][1]+trca))*prodcost[2][0]
                            if prodcost[1][0] > 0:
                                bpsubp =(np.mean(BPpricedata[idx])-(prodcost[1][1]+trcp)                                +(np.mean(Ppricedata[idx])-(prodcost[2][1]+trca))*prodcost[2][0]/prodcost[1][0])*prodcost[1][0]
                            else:
                                bpsubp = 0
                            if prodcost[2][0] > 0:
                                psubbp =(np.mean(Ppricedata[idx])-(prodcost[2][1]+trca)                                +(np.mean(BPpricedata[idx])-(prodcost[1][1]+trcp))*prodcost[1][0]/prodcost[2][0])*prodcost[2][0]
                            else:
                                psubbp = 0
                            if nosub > psubbp and nosub >= bpsubp:
                                inv = 'BAU'
                                prof = nosub +(Elr[idx]-(prodcost[0][1]+prodcost[3][1]))*(prodcost[0][0]+prodcost[3][0])
                            if psubbp >= nosub and psubbp >= bpsubp:
                                inv = 'PS'
                                prof = psubbp+(Elr[idx]-(prodcost[0][1]+prodcost[3][1]))*(prodcost[0][0]+prodcost[3][0])
                            if bpsubp >= nosub and bpsubp >= psubbp:
                                inv = 'BPS'
                                prof = bpsubp+(Elr[idx]-(prodcost[0][1]+prodcost[3][1]))*(prodcost[0][0]+prodcost[3][0])
                            else:
                                inv = 'BAU'
                                prof = nosub+(Elr[idx]-(prodcost[0][1]+prodcost[3][1]))*(prodcost[0][0]+prodcost[3][0])
                            Profit.append((prof,u,comb,inv,a,p))
                elif 'BP' not in comb and 'P' not in comb:
                    prof = (Elr[idx]-(prodcost[0][1]+prodcost[3][1]))*(prodcost[0][0]+prodcost[3][0])
                    Profit.append((prof,u,comb,inv,a,p))
        Profityear[yr] = Profit


# In[12]:

#Sort most profitable
combdyear = {}
for year, Profit in Profityear.items():
    MP = sorted(Profit, key=lambda x:x[0], reverse=True)
    combd = {}
    for rank in MP:
        proft = rank[0]
        u = rank[1]
        comb = rank[2]
        inv = rank[3]
        a = rank[4]
        p = rank[5]
        if u not in combd.keys():
            combd[u] = (comb,inv,proft,a,p)
    combdyear[year] =combd.copy()


# In[13]:

import csv

csvfile = "C:\\Users\\Dirk-Jan\\Dropbox\\DJ\\Python\\EU_P_BP_E\\Data.csv"
#Assuming res is a flat list
with open(csvfile, "w") as output:
    writer = csv.writer(output, lineterminator='\n')
    n=0
    writer.writerow(['Technology combinations:']+combinations) 
    writer.writerow(['#','x','y']+yearsl+yearsl+yearsl) 
    for u in U.nodes():
        n=n+1
        config = []
        subs = []
        proft = []
        for year,combd in combdyear.items():
            config.append(combd[u][0])
            subs.append(combd[u][1])
            proft.append(combd[u][2])
        writer.writerow([n,round(u[0],3),round(u[1],3)]+config+subs+proft)    


# # Mapping (In Development)

# In[ ]:

#Make position library (coordinates of all nodes)
pos4326 = {}
for u in U.nodes():
    pos4326[u] = u
for d in DDdef.values()
    for k in d.nodes():
        pos4326[k] = k
# Define colors for recovery combinations
#combinations = [['E1','P','E2'],['E1','P',],['E1'],['E1','E2'],
                #['BP','P','E2'],['BP','P'],['BP'],['BP','E2'],
                #['P','E2'],['E2'],['P'],['N']]
colordict{1:'green',2:'orange',3:'blue',4:'red'} #1: P recovery, 2: BP recovery, 3:electricyt recovery, 4: no recovery


# In[ ]:

MP = sorted(combdyear[2015].items(), key=lambda x:x[1][0], reverse=True)
m = Basemap(projection='cea',llcrnrlat=-90,urcrnrlat=90,llcrnrlon=-180,urcrnrlon=180,resolution='c',epsg=4326)
m.drawcoastlines(linewidth=0.05)
R = nx.Graph()
for nl in MP:
    if 'P' in nl[2] and 'BP' not in nl[2]:
        nx.draw_networkx_nodes(R, pos=pos4326, nodelist=[nl[0]], node_color=colordict[1], node_size=1)
    if 'BP' in nl[2] and 'P' not in nl[2]:
        nx.draw_networkx_nodes(R, pos=pos4326, nodelist=[nl[0]], node_color=colordict[2], node_size=1)
    if 'E1' in nl[2] or 'E2' in nl[2] and ('P' not in nl[2] or 'BP' not in nl[2]):
        nx.draw_networkx_nodes(R, pos=pos4326, nodelist=[nl[0]], node_color=colordict[3], node_size=1)  
    elif 'E1' not in nl[2] and 'E2' not in nl[2] and 'P' not in nl[2] and 'BP' not in nl[2]:
        nx.draw_networkx_nodes(R, pos=pos4326, nodelist=[nl[0]], node_color=colordict[4], node_size=1)
plt.axis('off')


# In[ ]:

def mapmaking(yeardict, dpi):
    for i in 
    
        Nodelist = Nodedict[str(year)][0]
        for n in Nodelist:
            if n[0] == 'Urban':
                r=0
                if (('P',n[1]) in yeardict[str(year)]['profit'].keys()):
                    Pprofit.append((n[1],'green'))    
                    r=r+1
                else:
                    Pprofit.append((n[1],'red'))
                if (('BP',n[1]) in yeardict[str(year)]['profit'].keys()):
                    BPprofit.append((n[1],'green'))
                    r=r+1
                else:
                    BPprofit.append((n[1],'red'))                     
                if (("E",n[1]) in yeardict[str(year)]['profit'].keys() and (yeardict[str(year)]['profit'][("E",n[1])]>0)):
                    Eprofit.append((n[1],'green')) 
                    r=r+1
                else:
                    Eprofit.append((n[1],'red'))                                                                           
                allp.append((n[1],r))
                pos4326[n[1]]=n[1]
                profitlists=[[Eprofit,'E'],[Pprofit,'P'],[BPprofit,'BP']]
        for ls in profitlists:
            plt.title(labelleg[ls[1]][0]+" "+str(year)) 
            m = Basemap(projection='cea',llcrnrlat=-90,urcrnrlat=90,
                        llcrnrlon=-180,urcrnrlon=180,resolution='c',epsg=4326)
            m.drawcoastlines(linewidth=0.05)
            R = nx.Graph()
            nx.draw_networkx_nodes(R, pos=pos4326, nodelist=[it[0] for it in ls[0]], node_color=[it[1] for it in ls[0]], node_size=1)                     
            plt.axis('off')
            #plt.title(str(name)+": "+str(round(price))+"[$]; "+str(round(TradedIteral,2))+"[MtP]"
            plt.savefig("C:\\Users\\Dirk-Jan\\Desktop\\MapsDynamic\\"+ls[1]+"\\"+str(year)+".png",dpi=dpi)
            plt.close()
            R.clear()

        plt.title("Composite "+str(year))
        G = nx.Graph()
        m = Basemap(projection='cea',llcrnrlat=-90,urcrnrlat=90,
                    llcrnrlon=-180,urcrnrlon=180,resolution='c',epsg=4326)
        m.drawcoastlines(linewidth=0.05)

        nx.draw_networkx_nodes(G, pos=pos4326, nodelist=[i[0] for i in allp], node_color=[colordict[i[1]] for i in allp], node_size=1)                     
        plt.axis('off')
        #plt.title(str(name)+": "+str(round(price))+"[$]; "+str(round(TradedIteral,2))+"[MtP]"
        plt.savefig("C:\\Users\\Dirk-Jan\\Desktop\\MapsDynamic\\Composite\\"+str(year)+".png",dpi=dpi)
        G.clear()


# # Price charts (In Development)

# In[ ]:

def charts(nodedict,year):
    UrbNodes = nodedict[year][0]
    idx = yearsl.index(year)
    plt.close()
    BPE1 = [round(u[1][1]*100) for u in UrbNodes]
    BPE21 = [round(u[2][0][1]*100) for u in UrbNodes]
    BPE22 = [round(u[2][1][1]*100) for u in UrbNodes]
    BPE23 = [round(u[2][2][1]*100) for u in UrbNodes]
    BPP = [u[3][1] for u in UrbNodes]
    BPBP = [u[4][1] for u in UrbNodes]
    boxplots = {}
    boxplots['BPE'] = [BPE1,BPE21,BPE22,BPE23,El[idx]]
    boxplots['BPP'] = [BPP,Ppricedata[idx]]
    boxplots['BPBP'] = [BPBP,BPpricedata[idx]]

    labeldic={} #[0]Title/y-acis,  [1] boxplot labels, [2] color definition
    labeldic['BPE'] = ['Electricity recovery Cost [¢/kWh]',['Inc. recov.','Biogas T1','Biogas T2','Biogas T3','Electricity'],['darkred','cyan','darkcyan','darkslategrey','grey']]
    labeldic['BPP'] = ['Phosphorus recovery Cost [$/t]',['Struvite','DAP Market Prices'],['darkslategrey','grey']]
    labeldic['BPBP'] = ['Biopolymer recovery Cost [$/t]',['PHA','PP'],['darkslategrey','grey']]

    for key,item in boxplots.items():
        plt.close()
        plt.figure(figsize=(5,5))
        labels2 = labeldic[key][1]
        plt.ylabel(labeldic[key][0])
        bplot=plt.boxplot(item,vert=True,  # vertical box alignment
                         patch_artist=True,  # fill with color
                         widths=0.7,
                         labels=labels2,
                         whis = 100,
                         showfliers=False)  # will be used to label x-ticks)
        for patch, color in zip(bplot['boxes'], labeldic[key][2]):
            patch.set_facecolor(color)
        if key == 'BPE':
            plt.ylim(0,60)
        plt.title(labeldic[key][0])
        #plt.savefig(key+'.pdf', dpi= 200)
        plt.show()
        plt.clf()


# In[ ]:


#Define colors for each to be used in creating graphs and maps
colordict = {}
colordict['Urban'] = 'dodgerblue'
colordict[1] = 'cyan'
colordict[2] = 'darkcyan'
colordict[3] = 'slategrey'
colordict['Agriculture'] = 'darkgreen'
colordict[-1] = 'darkgreen'
colordict['Plastics'] = 'orange'
colordict[-2] = 'orange'

