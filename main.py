from bs4 import BeautifulSoup
import requests
import csv
import pandas


rolePlayers = ['Portieri','Difensori','Centrocampisti','Trequartisti','Attaccanti']
df = pandas.read_csv('lista.csv')
listName = df['Nome']
df.set_index("Nome", inplace=True)

for role in rolePlayers:
    print(role)
    page = requests.get("https://www.fantacalciopedia.com/lista-calciatori-serie-a/"+role.lower()+"/")
    soup = BeautifulSoup(page.content, 'html.parser')

    mydivs = soup.find_all("div", {"class": "col_full giocatore"})
    if role != 'Attaccanti':
        dictPlayer = {}
    for playersPage in mydivs:
        meanSkill = 0
        hrefPlay = playersPage.find_all("a",{"class":"label label-default fondoindaco"})[0]['href']
        ruoloSite = role[0]
        if ruoloSite == 'T':
            ruoloSite = 'A'

        namePlay = playersPage.find("h3",{"class":"tit_calc"})
        newPage = requests.get(hrefPlay)
        soupInfo = BeautifulSoup(newPage.content, 'html.parser')
        values = soupInfo.find_all("div", {"class": "label12"})
        appVal = str(values[4].text).split(":")
        teamSite = appVal[len(appVal)-1].replace("\n","").replace(" ","")
        print(teamSite)
        skillsPlayer = soupInfo.find_all("ul", {"class": "skills"})
        for skillsUl in skillsPlayer:
            skillsLi = skillsUl.find_all("li")
            for skillLi in skillsLi:
                skillsDiv = skillLi.find_all("div",{"class":"counter counter-inherit counter-instant"})
                for skillDiv in skillsDiv:
                    skillsSpan = skillDiv.find_all("span")
                    for skill in skillsSpan:
                        meanSkill += int(skill.text)
        dictPlayer[str.lower(namePlay.text)] = {"Media":meanSkill/4,"Ruolo":ruoloSite,"Squadra":teamSite}

    if role != 'Trequartisti':
        dictPlayer = sorted(dictPlayer.items(), key=lambda x: x[1]['Media'], reverse=True)
        if role == 'Trequartisti':
            role = 'Attaccanti'
        with open('meanSkill'+role+'.csv', 'a+',newline='') as f:
            # create the csv writer
            writer = csv.writer(f)
            for key, value in dictPlayer:
                flag = 0
                for name in listName:
                    namePlayer = str(name).replace('.','').replace('-',' ').lower()
                    team = df.loc[[name]]['Squadra'][name]
                    ruolo = df.loc[[name]]['R'][name]
                    ruoloSite = value['Ruolo']
                    teamSite = value["Squadra"]
                    if namePlayer in key and ruolo == ruoloSite and team == teamSite:
                        print(name,team,ruolo)
                        writer.writerow([name,team,ruolo,value['Media']])
                        flag = 1
                        break
                if flag == 0:
                    ruoloSite = value['Ruolo']
                    teamSite = value["Squadra"]
                    writer.writerow([str(key).upper(),teamSite,ruoloSite,value['Media']])


