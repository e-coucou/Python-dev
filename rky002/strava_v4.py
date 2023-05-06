#!/usr/bin/python
# -*- coding: utf-8 -*-
import stravalib
# import BaseHTTPServer
from http.server import BaseHTTPRequestHandler,HTTPServer
from urllib import urlparse
import webbrowser
import pandas as pd
from datetime import *
import requests, lxml, json, urllib, sys, argparse, getpass, time, math

ep_id = 24888739
#Global Variables - put your data in the file 'client.secret' and separate the fields with a comma!
client_id, secret = open('client.secret').read().strip().split(',')
print(client_id)
print(secret)
port = 5050
url = 'http://localhost:%d/authorized' % port
allDone = False
types = ['time', 'distance', 'latlng', 'altitude', 'velocity_smooth', 'moving', 'grade_smooth', 'temp']
limit = 5
DEBUG = 0
FORCE = 0
url_activities = "https://www.strava.com/api/v3/athlete/activities/"
url_athlete = "https://www.strava.com/api/v3/athletes/" 
url_list = "https://www.strava.com/api/v3/activities/"
url_segment = "https://www.strava.com/api/v3/segment_efforts/"
h1 = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'}

#Create the strava client, and open the web browser for authentication
client = stravalib.client.Client()
authorize_url = client.authorization_url(client_id=client_id, redirect_uri=url)
print('Opening: %s' % authorize_url)
webbrowser.open(authorize_url)
def copyright():
    print("-----------------------------------------------------------------------------------")
    print("Strava extraction pour calculer les performances de courses (run) : Bannister/TRIMP")
    print("---------------------------")
    print("(c) eCoucou - janvier 2018")
    print("v0.1 release 02 - 01/2018")
    print("v0.1 release 03 - 02/2018")
    print("---------------------------")
def get_config():
    global HR_MAX, HR_REST, HRr, client_id, client_secret, p, DEBUG, email, password
    try:
        config = json.load(open('config.json'))
        print("Bonjour ",config['Nom'])
        DEBUG = config['DEBUG']
        HR_MAX = config['HRMax']
        HR_REST = config['HRrepos']
        if (config['Genre']=='H'):
            HRr = 1.92
        else:
            HRr = 1.84
        client_secret = config['client_secret']
        client_id = config['client_id']
        if (config['proxy_detail']['PROXY_ON'] == 1):
            p = config['proxy_detail']['proxy']
        else :
            p = {}
        email = config["strava"]["email"]  #"eric@plaidy.net"
        password = config["strava"]["password"] #"Ricky03!"
    except:
        print("no config file")
    return
def get_args():
    global p, args
    global DEBUG, VERBOSE, FORCE, client_id, client_secret,per_page
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description='Liste les activites STRAVA dans un fichier csv')
    parser.add_argument("-p","--proxy",default={},help="si vous etes derriere un proxy -> proxy:port")
    parser.add_argument("-e","--email",default='first.name@my-org.com',help="adresse mail")
    parser.add_argument("-d","--debug",default=False,action="store_true", help="=1 en mode DEBUG")
    parser.add_argument("-M","--PassStrava",default='XYZ!',help="Mot de Passe STRAVA")
    parser.add_argument("-s","--client_secret",default='',help="clé Strava : client_secret")
    parser.add_argument("-i","--client_id",default='',help="Identifiant Strava : client_id")
    parser.add_argument("-O","--Outside",default= False , action="store_true" ,help="=1 en mode Externe")
    parser.add_argument("-U","--username",default="EPlaidy",help="username du proxy")
    parser.add_argument("-P","--Password",default="",help="password du Proxy")
    parser.add_argument("-v","--verbose",default=False,action="store_true",help="toutes les infos ...")
    parser.add_argument("-f","--force",default=False,action="store_true",help="force le recalcul de toutes les activités")
    parser.add_argument("-n","--nombre",default=10,help="nombre d'activite")
    args = parser.parse_args()
    DEBUG = args.debug
    VERBOSE = args.verbose
    FORCE = args.force
    proxy = args.proxy
    per_page = args.nombre
    if (args.proxy != {} ) :
        Password = args.Password
        if args.Password == "" :
            Password = getpass.getpass(prompt="Entrez votre mot de passe Windows")
        proxy = args.username+':'+Password+'@'+args.proxy
        p={'http': 'http://'+proxy , 'https':'https://'+proxy}
    if (args.client_secret != ''):
        client_secret = args.client_secret
    else :
        if client_secret == '' :
            client_secret = getpass.getusername(prompt="Entrez le client secret STRAVA :")
    if args.client_id != '' :
        client_id = args.client_id
    else :
        if client_id == '' :
            client_id = getpass.getusername(prompt="Entrez le client id STRAVA :")
    # if VERBOSE :
    #     #       print auth.username, auth.password
    #     print('--------------------------------------------------------------------------')
    #     aff('Arguments ...','')
    #     aff('Username      :',args.username)
    #     aff('eMail         :',args.email)
    #     aff('proxy : ',proxy)
    # return
def max(a,b):
    if (a >= b):
        return a,0
    else:
        return b,1
def mobile(p_d,p_t,n):
    nb = len(p_d)
    p_m = 0
    for i in range(nb-n):
        p_d_s = 0
        p_t_s = 0
        for j in range(n):
            p_d_s += p_d[i+j]
            p_t_s += p_t[i+j]
        if (p_d_s >= (n*1000.0 * 0.95)):
            p_m,chg = max(p_m,(p_d_s / p_t_s)*3.6)
    return p_m
#Define the web functions to call from the strava API
def UseCode(code):
    global access_token
    if VERBOSE:
        print(client_id, client_secret, code)
    u = 'https://www.strava.com/oauth/token?client_id=%s&client_secret=%s&code=%s' % (client_id, client_secret, code)
    c = {}
    print(u)
    r = s.post(u, verify = True,allow_redirects=True, headers= h1, cookies = c, proxies= p)
    access_token = json.loads(r.text)['access_token']
    if VERBOSE:
        print("code Temporaire: ",access_token)
	
	#Retrieve the login code from the Strava server
#	access_token = client.exchange_code_for_token(client_id=client_id,client_secret=secret, code=code)
#	print access_token
	# Now store that access token somewhere (for now, it's just a local variable)
    client.access_token = access_token
    return client

def GetActivities(client,limit):
    #Returns a list of Strava activity objects, up to the number specified by limit
    activities = client.get_activities(limit=limit)
    assert len(list(activities)) == limit
    for item in activities:
        print(item)
    return activities
""" --- Athlete sur STRAVA ----------------------------------------------------"""
def get_athlete():
    global jAthlete
    print("- athlete : --------------------------------")
    u = url_athlete+str(ep_id)+'?access_token='+access_token
    d = { "Authorization" : access_token}
    r = s.get(u, verify = True,allow_redirects=True, headers= h1, data = d, proxies= p)
    jAthlete = json.loads(r.text)
    if DEBUG :
        print(jAthlete)
    print("%s [%d]" % (jAthlete['lastname'],jAthlete['id']))
    print("%s (%s)" % (jAthlete['city'],jAthlete['state']))
    print("Poids : %4.1f kg" % (jAthlete['weight']))
    for shoes in jAthlete['shoes']:
        print("  .%s -> %4.0f km" % (shoes['name'],shoes['distance']/1000.0))
    print("--------------------------------------------")
    return
""" --- Activite sur STRAVA ----------------------------------------------------"""
def new_activite(ji,dict_activite,dict_athlete):
    day = datetime.strptime(ji['start_date'][0:10],"%Y-%m-%d")
    jour = day.strftime("%d/%m/%Y")
    run = ji['type']
    distance = ji['distance']
    duree = ji['moving_time']
    if VERBOSE :
        print('nouvelle activite')
        print(jour)
        print('-- Type     : ',ji['type'])
        print('-- Start    : ',day.strftime("%d/%m/%Y"))
        print('-- Distance : ',ji['distance'])
        print('-- Duree    : ',ji['moving_time'])
        print("-- Vitesse  : %4.1f km/h" % (ji['average_speed']*3.6))
    isHR = ji['has_heartrate']
    if (isHR) :
        HR_moy = ji['average_heartrate']
        suffer = ji['suffer_score']
        cadence = ji['average_cadence']
        if (ji['external_id'].find('garmin') != -1) :
            cadence = cadence * 2.0
        ratio = (HR_moy-HR_REST)/(HR_MAX-HR_REST)
        TRIMPexp = ji['moving_time']/60.0 * ratio * 0.64 * math.exp(1.92*ratio)
        if VERBOSE:
            print('-- HR       : ',HR_moy)
            print('-- Suffer   : ',suffer)
            print('-- Cadence  : ',cadence)
            print('-- TRIMPexp : %6.2f' % (TRIMPexp))
        dict_activite['TRIMP'] = TRIMPexp
        dict_activite['HR'] = HR_moy
        dict_activite['suffer'] = suffer
        dict_activite['cadence'] = cadence
        dict_activite['type'] = run
        dict_activite['distance'] = distance
        dict_activite['duree'] = duree
        dict_activite['jour'] = jour
    # Detail de l'activite ...
    uL=url_list + str(ji['id'])+'?access_token='+access_token+'&include_all_efforts=true'
    rL = s.get(uL, verify = True,allow_redirects=True, headers= h1, proxies= p)
    jL = json.loads(rL.text)
    TRIMPexpA=0
    p_10km = 99999999.9 # performance sur 10km
    p_nb =0
    p_metrics_d = []
    p_metrics_t = []
    try:
        #       print jL['average_cadence']
        p_distance = 0
        p_temps = 0
        for jLm in jL['splits_metric']:
            if DEBUG :
                print(jLm)
            p_distance +=  jLm['distance']
            p_temps += jLm['moving_time']
            p_nb += 1
            p_metrics_d.append(jLm['distance'])
            p_metrics_t.append(jLm['moving_time'])
            if VERBOSE:
                print ("%d - %6.1f [%6.2f]") % (jLm['moving_time'], jLm['distance'], jLm['distance']/(jLm['moving_time']/3600.0)/1000.0)
            ratio = (jLm['average_heartrate']-HR_REST)/(HR_MAX-HR_REST)
            TRIMPexpi = jLm['moving_time']/60.0 * ratio * 0.64 * math.exp(1.92*ratio)
            if VERBOSE :
                print(jLm['pace_zone'],jLm['average_heartrate'])
                print('%6.1f m / %5d s / %6.3f HR / %2d / %6.3f'%(jLm['distance'],jLm['moving_time'],jLm['average_heartrate'],jLm['pace_zone'],TRIMPexpi))
            TRIMPexpA = TRIMPexpA + TRIMPexpi
        if VERBOSE:
            print('-- TRIMPexpA: %6.2f'%(TRIMPexpA))
            #print p_temps, p_distance, p_distance/(p_temps/3600.0)/1000.0
            print("nb metrics %d" % (p_nb))
        dict_athlete['PR']['1km']['value'],chg = max(dict_athlete['PR']['1km']['value'],mobile(p_metrics_d,p_metrics_t,1))
        if (chg):
#            print "record 1"
            dict_athlete['PR']['1km']['activite'] = ji['id']
            dict_athlete['PR']['1km']['date'] = jour
            dict_athlete['PR']['1km']['course'] = p_distance/1000.0
            val = (3600.0/dict_athlete['PR']['1km']['value'])
            dict_athlete['PR']['1km']['rythme'] = str(timedelta(seconds=val))
        dict_athlete['PR']['2km']['value'],chg = max(dict_athlete['PR']['2km']['value'],mobile(p_metrics_d,p_metrics_t,2))
        if (chg):
#           print "record 2"
            dict_athlete['PR']['2km']['activite'] = ji['id']
            dict_athlete['PR']['2km']['date'] = jour
            dict_athlete['PR']['2km']['course'] = p_distance/1000.0
            val = (3600.0/dict_athlete['PR']['2km']['value'])
            dict_athlete['PR']['2km']['rythme'] =str(timedelta(seconds=val*2))
        dict_athlete['PR']['5km']['value'],chg = max(dict_athlete['PR']['5km']['value'],mobile(p_metrics_d,p_metrics_t,5))
        if (chg):
#           print "record 5"
            dict_athlete['PR']['5km']['activite'] = ji['id']
            dict_athlete['PR']['5km']['date'] = jour
            dict_athlete['PR']['5km']['course'] = p_distance/1000.0
            val = (3600.0/dict_athlete['PR']['5km']['value'])
            dict_athlete['PR']['5km']['rythme'] = str(timedelta(seconds=val*5))
        dict_athlete['PR']['10km']['value'],chg = max(dict_athlete['PR']['10km']['value'],mobile(p_metrics_d,p_metrics_t,10))
        if (chg):
#            print "record 10"
            dict_athlete['PR']['10km']['activite'] = ji['id']
            dict_athlete['PR']['10km']['date'] = jour
            dict_athlete['PR']['10km']['course'] = p_distance/1000.0
            val = (3600.0/dict_athlete['PR']['10km']['value'])
            dict_athlete['PR']['10km']['rythme'] = str(timedelta(seconds=val*10))
        dict_athlete['PR']['15km']['value'],chg = max(dict_athlete['PR']['15km']['value'],mobile(p_metrics_d,p_metrics_t,15))
        if (chg):
#            print "record 15"
            dict_athlete['PR']['15km']['activite'] = ji['id']
            dict_athlete['PR']['15km']['date'] = jour
            dict_athlete['PR']['15km']['course'] = p_distance/1000.0
            val = (3600.0/dict_athlete['PR']['15km']['value'])
            dict_athlete['PR']['15km']['rythme'] = str(timedelta(seconds=val*15))
        dict_athlete['PR']['20km']['value'],chg = max(dict_athlete['PR']['20km']['value'],mobile(p_metrics_d,p_metrics_t,20))
        if (chg):
#            print "record 20"
            dict_athlete['PR']['20km']['activite'] = ji['id']
            dict_athlete['PR']['20km']['date'] = jour
            dict_athlete['PR']['20km']['course'] = p_distance/1000.0
            val = (3600.0/dict_athlete['PR']['20km']['value'])
            dict_athlete['PR']['20km']['rythme'] = str(timedelta(seconds=val*20))
        dict_activite['TRIMP_A'] = TRIMPexpA
    except:
        print(' - no metric -')
    if ((run == "Run") & isHR):
        s_ = "%s;%d;%6.2f;%d;%6.2f;%f;%f;%6.2f;%6.2f;\n" % (jour,ji['id'],distance,duree,HR_moy,suffer,cadence,TRIMPexp,TRIMPexpA)
        f.write(s_.replace('.',','))
        if VERBOSE:
            print("on ecrit le fichier csv ...")
            print(dict_activite)
        dict_athlete[str(ji['id'])] = dict_activite
    return
def get_activite():
    # lecture du fichier enregistre précedemment
    global isHR
    out_name = jAthlete['username']+'.json'
    run = ''
    n_lec = per_page
    isHR = False
    try :
        dict_athlete = json.load(open(out_name))
        if VERBOSE :
            print(dict_athlete)
    except :
        dict_athlete = {}
        dict_athlete['nom'] = jAthlete['username']
        dict_athlete['PR'] = {}
        dict_athlete['PR']['1km'] = {'value':0}
        dict_athlete['PR']['2km'] = {'value':0}
        dict_athlete['PR']['5km'] = {'value':0}
        dict_athlete['PR']['10km'] = {'value':0}
        dict_athlete['PR']['15km'] = {'value':0}
        dict_athlete['PR']['20km'] = {'value':0}
    page = 1
    count = 1
    dict_athlete['PR'] = {}
    dict_athlete['PR']['1km'] = {'value':0}
    dict_athlete['PR']['2km'] = {'value':0}
    dict_athlete['PR']['5km'] = {'value':0}
    dict_athlete['PR']['10km'] = {'value':0}
    dict_athlete['PR']['15km'] = {'value':0}
    dict_athlete['PR']['20km'] = {'value':0}
    print("- Activites : --------------------------------")
    while (n_lec>=per_page):
        u = url_activities+'?access_token='+access_token+'&per_page='+str(per_page)+'&page='+str(page)
        d = { "Authorization" : access_token}
        r = s.get(u, verify = True,allow_redirects=True, headers= h1, data = d, proxies= p)
        j = json.loads(r.text)
        n_lec = len(j)
        if DEBUG :
            print(j)
        if VERBOSE:
            print("%d activites listees." % (n_lec))
        for ji in j:
            dict_activite = {}
            print('--',count,'/',ji['id'],'------------------------------------------------')
            if VERBOSE:
                print(ji)
            try:
                activite = ji['id']
                yet = dict_athlete.get(str(activite),'none')
                if ((yet == 'none') | FORCE) :
                    new_activite(ji,dict_activite,dict_athlete)
                    print(dict_athlete[str(activite)])
                else :
                    print(dict_athlete[str(activite)])
            except:
                print(' - no data - // ERROR !')
                print(dict_activite)
            count += 1
        page += 1
    if VERBOSE :
        print(dict_athlete)
    print(dict_athlete)
    for PR in dict_athlete['PR']:
        print(PR)
    json.dump(dict_athlete,open(out_name,'w'))
    return
def GetStreams(client, activity, types):
    #Returns a Strava 'stream', which is timeseries data from an activity
    streams = client.get_activity_streams(activity, types=types, series_type='time')
    return streams

def DataFrame(dict,types):
    #Converts a Stream into a dataframe, and returns the dataframe
    print(dict, types)
    df = pd.DataFrame()
    for item in types:
        if item in dict.keys():
            df.append(item.data)
    df.fillna('',inplace=True)
    return df

def ParseActivity(act,types):
    act_id = act.id
    name = act.name
    print(str(act_id), str(act.name), act.start_date)
    streams = GetStreams(client,act_id,types)
    df = pd.DataFrame()

    #Write each row to a dataframe
    for item in types:
        if item in streams.keys():
            df[item] = pd.Series(streams[item].data,index=None)
        df['act_id'] = act.id
        df['act_startDate']= pd.to_datetime(act.start_date)
        df['act_name'] = name
    return df

def calctime(time_sec, startdate):
    try:
        timestamp = startdate + datetime.timedelta(seconds=int(time_sec))
    except:
        print('time processing error : ' + str(time_sec))
        timestamp = startdate
    return timestamp

def split_lat(series):
    lat = series[0]
    return lat

def split_long(series):
    long = series[1]
    return long

def concatdf(df_lst):
    return pd.concat(df_lst, ignore_index=False)

class MyHandler(BaseHTTPRequestHandler):
  #Handle the web data sent from the strava API
  def do_HEAD(self):
    return self.do_GET()

  def do_GET(self):
    #Get the API code for Strava
    self.wfile.write('<script>window.close();</script>')
    code = urlparse.parse_qs(urlparse.urlparse(self.path).query)['code'][0]
    print(self.path)

    #Login to the API
    client  = UseCode(code)

    get_athlete()
    get_activite()
    #Retrieve the last limit activities
#    activities = GetActivities(client,limit)

    #Loop through the activities, and create a dict of the dataframe stream data of each activity
    print("looping through activities...")
#    df_lst = {}
#    for act in activities:
#        print act.name
#        df_lst[act.start_date] = ParseActivity(act,types)

    #create the concatenated df and fill null values
#    df_total = concatdf(df_lst)
#    df_total.fillna('',inplace=True)

    #Calculate the timestamp column
#    df_total = df_total.reset_index(level=0)
#    df_total['timestamp'] = pd.to_datetime(map(calctime, df_total['time'], df_total['level_0'])).to_pydatetime()

    #Split out lat and long columns
#    df_total['lat'] = map(split_lat, (df_total['latlng']))
#    df_total['long'] = map(split_long, (df_total['latlng']))

    #Index by startdate and timestamp, and drop arbitrary columns
#    df_total = df_total.set_index(['act_startDate','timestamp'])
#    df_total.drop(['latlng', 'level_0'], axis=1, inplace=True)

    #Write the file to a CSV - this will end up in your working directory
#    now = datetime.datetime.now()
#    df_total.to_csv('RideData_' + str(now.strftime('%Y%m%d%H%M%S')) + '.csv')
    print('script complete!')
    f.close()

if __name__=='__main__':
###Run the program to login and grab data###
    copyright()
    get_config()
    get_args()
    if (FORCE):
        f = open('trimp.csv','w')
    else:
        f = open('trimp.csv','a')
    s = requests.Session()
    try:
        httpd = HTTPServer(('localhost', port), MyHandler)
        print("handle_request -> ouverture du serveur local !")
        httpd.handle_request()
    except KeyboardInterrupt:
                    # Allow ^C to interrupt from any thread.
                    f.close()
                    sys.stdout.write('\033[0m')
                    sys.stdout.write('User Interupt\n')