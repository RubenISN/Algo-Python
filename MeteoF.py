#!/usr/bin/env python
#-*- coding: utf-8 -*-
from BeautifulSoup import *
import requests
import smtplib
import sys
import serial
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import time

brouillard = '001001001001001001010010010100100100100100100010010010001001001001001001010010010100100100100100100010010010001001001001001001'
pluie = '000000000000000000000110000001001001001001010010001101100001010100001101010001010010001100010001000001001000000110000000000000'
neige = '000000000000000000000010000010111010110010011001010100010111010111101111010111010001010100110010011010111010000010000000000000'
soleil = '000000000000000000000000000000010000010000010000111000001111100101111101001111100000111000010000010000010000000000000000000000'
orage = '001000000011010000101100000001000000000010000000110000001010010010010100000011000000010000000000100000001101000010110000000100'
nuage = '000011100000100010000100001000100001011010001100000001100000001100000001100000001010010001001100001000100010000100010000011100'

s = serial.Serial()
s.baudrate = 9600
s.timeout = 0
s.port = "/dev/serial0"

try:
    s.open()
except serial.SerialException, e:
    sys.stderr.write("could not open port %r: %s\n" % (s.port, e))
    sys.exit(1)

s.write("$$$ALL,OFF\r")
			
def AffichageTkinter(TempsEN, visibilite, degres, humidite, degresMin, degresMax, pression, Temps, Vvent, direcVent, DistVisibilite, ville, ConnectNetwork, PresenceVent, Alerte, destinataire, password, ConfirmMailSend):
	if ConnectNetwork==1:
		#Nous devons supprimer les messages précédents
		Efface = Label(app, text=" 																									").place(x=110,y=140)
		Efface = Label(app, text=" 																									").place(x=110,y=170)	
		Efface = Label(app, text=" 																									").place(x=110,y=190)	
		Efface = Label(app, text=" 																									").place(x=80,y=210)	
		Efface = Label(app, text=" 																									").place(x=110,y=230)
		Efface = Label(app, text=" 																									").place(x=132 ,y=250)
		Efface = Label(app, text=" 																									").place(x=132 ,y=270)


		#Etat du systeme (connexion) donc ici fonctionnel
		EtatSysteme = Label(app, text="Etat :", font=("Helvetica", 9)).place(x=235 ,y=140)
		Fonctionnel = Label(app, text="Fonctionnel", fg="darkgreen", font=("Helvetica", 9)).place(x=265 ,y=140)

		#Affichage de toute les donnees recuperees et traitees
		Temperature = Label(app, text=("La temperature a "+str(ville)+" est de: "+str(degres)+" degres .")).place(x=168,y=170)	
		ConditionMeteo = Label(app, text=("Le temps est "+str(Temps)+".  ")).place(x=221,y=190)	
		temperatureMinMax = Label(app, text=("La temperature maximal du jour de "+str(degresMax)+" degres et descendra jusqu'a "+str(degresMin)+" degres .")).place(x=70,y=210)
		Humidite = Label(app, text=("L'humidite a "+str(ville)+" est de: "+str(humidite)+"% et la pression est de "+str(pression)+" PA .  ")).place(x=30,y=230)	
		if PresenceVent == 1:
			Vent = Label(app, text=("Le vent souffle a "+str(Vvent)+"km/h et de la direction "+str(direcVent)+".  ")).place(x=132,y=250)
		else:
			NoVent = Label(app, text=("Le vent est quasiment inexistant ")).place(x=195,y=250)
		Visibilite = Label(app, text=("La visibilite actuelle est "+str(DistVisibilite)+".")).place(x=195,y=270)


	else:
		#Nous devons supprimer les messages précédents
		Efface = Label(app, text="																						").place(x=110,y=190)	
		Efface = Label(app, text="																						").place(x=110,y=210)	
		Efface = Label(app, text="																						").place(x=110,y=230)
		Efface = Label(app, text="                                                                                                ").place(x=132 ,y=250)
		Efface = Label(app, text="                                                                                                ").place(x=132 ,y=270)

		#Etat du systeme (connexion) donc ici non-fonctionnel
		EtatSysteme = Label(app, text="Etat :", font=("Helvetica", 9)).place(x=164 ,y=140)
		Erreur = Label(app, text="Une erreur de connexion s'est réalise !", fg="red", font=("Helvetica", 9)).place(x=200 ,y=140)
		affichage1 = Label(app, text=("-----------------------------------------------------------------------")).place(x=110,y=170)

										
	#En cas d'alerte meteo envoyer les confirmations d'envois ou non du mail
	if Alerte ==1:
		if ConfirmMailSend ==1:
			ConfirmMailSend = Label(app, text="Une/Des alerte(s) est/sont envoyee(s) par mail !", fg="red", font=("Helvetica", 9)).place(x=154, y= 290)
		elif ConfirmMailSend ==0:
			ConfirmMailNoSend = Label(app, text="Impossible de se connecter a la boite mail (Identifiants non-valide) !", fg="red", font=("Helvetica", 9)).place(x=124, y= 290)
		else: 
			ConfirmMailNoSend = Label(app, text="																									", fg="red", font=("Helvetica", 9)).place(x=124, y= 290)
	else:
		#Sinon on efface le message precedent
		Efface = Label(app, text=("																						")).place(x=110,y=290)
			
	app.after(120000, RecupInfoMeteo)	


def RecupInfoMeteo():

	visibilite = 0
	degres = 0
	humidite = 0
	degresMin = 0
	degresMax = 0
	pression = 0
	TempsEN = 0
	Temps = 0 
	Vvent = 0
	direcVent = 0
	DistVisibilite = 0
	ville = 0
	ConnectNetwork = 0
	PresenceVent = 0
	Alerte = 0
	destinataire = 0
	password = 0 
	ConfirmMailSend = 0
	try:
		ConnectNetwork = 1																	#Comfirmation de connection au net
		ville = EntryVille.get()															#Recupere le nom de la ville, du destinataire
		destinataire = EntryDestinataire.get()												# et du mot de passe saisir sur la zone Tkinder
		password = EntryPassword.get()	
		#ville = raw_input("Saisir votre ville (Francaise uniquement): ")					#Selection de la ville sans Tkinder
		Info = requests.get("http://api.openweathermap.org/data/2.5/weather?q="+ville+",fr&appid=41e0ba6f6d2d3f7db3f16960cd553e73").json()


																							#Recuperation des informations meteo de la ville
		
		temp = Info['main']['temp']															#Recuperation de la donnee temperature actuelle
		tempMax = Info['main']['temp_max']													#Recuperation de la donnee temperature maximale
		tempMin = Info['main']['temp_min']													#Recuperation de la donnee temperature minimale
		humidite = Info['main']['humidity']													#Recuperation de la donnee humidite
		pression = Info['main']['pressure']													#Recuperation de la donnee pression
		visibilite = Info['visibility']														#Recuperation de la donnee sur la distance de visibilite
		#Recuperer le nom de la ville permet tous simplement d'avoir la majuscule du nom propre si nous avons pas mit correctement la/les majuscule(s)
		ville = Info['name']	
							
		degres = temp-273																	#Conversion (Fahrenheit en Celsius)			
		degresMax = tempMax-273																# et arrondie a la deuxieme decimale	
		degresMin = tempMin-273
		degres = round(degres,1)
		degresMin = round(degresMin,1)
		degresMax = round(degresMax,1)
		
																							#Dictionnaire pour traduire 
		TempsEN = Info['weather'][0]['main']												# le temps prévu (Anglais en Francais)
		Temps = {}																			#Creation d'un tableau
		Temps['Rain']='pluvieux'															#Les differentes traductions possibles
		Temps['Clear']='degage'
		Temps['Snow']='enneige'
		Temps['Storm']='orageux'
		Temps['Clouds']='nuageux'
		Temps['Mist']='brouillard'
		Temps['Thunderstorm']='tres orageux'
		
		s.write('La temperature a '+str(ville)+' est de '+str(degres)+' degres.') 
		time.sleep(15)

		if TempsEN =='Mist':
			s.write('Actuellement, il fait du brouillard.')
			time.sleep(16)
			s.write('$$$F' + brouillard + '\r')
			time.sleep(4)
		elif TempsEN =='Rain':
			s.write('Actuellement, il fait de la pluie.')
			time.sleep(16)	
			s.write('$$$F' + pluie + '\r')
			time.sleep(4)
		elif TempsEN =='Snow':
			s.write('Actuellement, il fait de la neige.')
			time.sleep(16)	
			s.write('$$$F' + neige + '\r')
			time.sleep(4)
		elif TempsEN =='Clear':
			s.write('Actuellement, il fait du soleil.')
			time.sleep(16)	
			s.write('$$$F' + soleil + '\r')
			time.sleep(4)
		elif TempsEN =='Storm' or Temps=='Thunderstorm':
			s.write('Actuellement, il fait de l orage.')
			time.sleep(16)
			s.write('$$$F' + orage + '\r')
			time.sleep(4)
		elif TempsEN =='Clouds':
			s.write('Actuellement, il fait nuageux.')
			time.sleep(16)
			s.write('$$$F' + nuage + '\r')
			time.sleep(4)
			

																							#Affichage sur le terminal des informations
		print("La temperature a "+ville+" est de: "+str(degres)+" degres .")				# sur le temps/ temperature/ humidité/ pression
		print("Le temps est "+Temps[TempsEN]+".")			
		print("La temperature maximal du jour de "+str(degresMax)+" degres et descendra jusqu'a "+str(degresMin)+" degres .")											
		print("L'humidite a "+ville+" est de: "+str(humidite)+"% et la pression est de "+str(pression)+" PA .")				
		Temps=Temps[TempsEN]
			
																							#Determination de la direction du vent (en degrès)
		try:
			PresenceVent = 1
			direcVent = Info['wind']['deg']													#Recuperation de la donnee direction du vent
																							#Si pas de vent alors le retour sera 
																							# consistué d'erreurs
			if 0<= direcVent  <=(90/4):														
				direcVent = "Nord"
			if (360-(90/4))< direcVent <=360:
				direcVent = "Nord"
			if (90-(90/4))< direcVent <= (90+(90/4)):
				direcVent = "Est"
			if (180-(90/4))< direcVent <= (180+(90/4)):
				direcVent = "Sud"
			if (270-(90/4))< direcVent <= (270+(90/4)):
				direcVent = "Ouest"
				
			if (90/4)< direcVent <= (90-(90/4)):
				direcVent = "Nord-Est"
			if (90+(90/4))< direcVent <= (180-(90/4)):
				direcVent = "Sud-Est"
			if (180+(90/4))< direcVent <= (270-(90/4)):
				direcVent = "Sud-Ouest"
			if (270+(90/4))< direcVent <= (360-(90/4)):
				direcVent = "Nord-Ouest"
				
			Vvent = Info['wind']['speed']													#Recuperation de la donnee vitesse du vent
																							#Si pas de vent alors le retour sera 
																							# consistué d'erreurs
			Vvent = Vvent*1.852																#Convertion noeuds -> Km/h
			Vvent = round(Vvent,2)															#Arrondie a 2 decimales


																							##Affichage sur le terminal des informations
																							# vitesse du vent / direction
			print("Le vent souffle a "+str(Vvent)+"km/h et de la direction "+str(direcVent)+" .")
																							#Si precedemment des erreurs sont survenus
		except:	
																							# alors cette partie sera réalisera.
			PresenceVent = 0
			print("Le vent ne souffle presque inexistant .")
			Vvent = 0
	


																							#Traitement de la variable Distance Visibilite
		if visibilite==10000:
			DistVisibilite=">10 000 m"
		else:
			DistVisibilite=("de "+str(visibilite)+"m")
		print("La visibilite actuelle est "+str(DistVisibilite)+".")

		app.after(10, Mail(TempsEN, visibilite, degres, humidite, degresMin, degresMax, pression, Temps, Vvent, direcVent, DistVisibilite, ville, ConnectNetwork, PresenceVent, destinataire, password))

		
	except:																					#Si erreurs de connexion (ou autre porbleme)
		ConnectNetwork = 0 	
		print("Une erreur de connexion est survenue")

def Mail(TempsEN, visibilite, degres, humidite, degresMin, degresMax, pression, Temps, Vvent, direcVent, DistVisibilite, ville, ConnectNetwork, PresenceVent, destinataire, password):																					#Envois du mail
																							#Systeme d'alerte qui s'active si 																			
	if visibilite<400 or degresMin<10 or Temps=='enneige' or Temps=='orageux' or Temps=='tres orageux' or Vvent>50:
		Alerte =1
		#Declaration des risques
		if visibilite<400:
			Alerte1='- Brouillard intense\n'
		else: Alerte1=''
		if 0<degresMin<10:
			Alerte2='- Temperature froide (comprise entre 0 et 10 degres (Celsius))\n'
		else: Alerte2=''
		if degresMin<1:
			Alerte3='- Verglas\n'
		else: Alerte3=''
		if Temps=='orageux' or Temps=='tres orageux':
			Alerte4='- Orage\n'
		else: Alerte4=''
		if Temps=='enneige':
			Alerte5='- Tombee de neige \n'
		else: Alerte5=''
		if Vvent>50:
			Alerte6='- Vents violents\n'
		else: Alerte6=''
				
				
				
				#Information du mail (Emetteur (facultatif) / Destinataire (facultatif)/ Objet / Corps)
				#Et redaction
		msg = MIMEMultipart()
		msg['From'] = destinataire
		msg['To'] = destinataire
		msg['Subject'] = '[ALERTE] STATION METEO' 
		message = ("[ALERTE METEO] Un risque est present a "+ville+", d'apres l'analyse qu'a realise votre station meteo, il semble qu'il y est des risques de : \n")
		msg.attach(MIMEText(message+Alerte1+Alerte2+Alerte3+Alerte4+Alerte5+Alerte6))
				
				#Element de connection a l'adresse mail de l'expediteur
				#password = 'NDV=2016' 
				#destinataire= 'ISN.NDV@gmail.com'
		try: 
			mailserver = smtplib.SMTP('smtp.gmail.com', 587)							#SMTP de Gmail (a changé si adresse differente de gmail)
			mailserver.starttls()														#Lancement a la connexion de la boite mail
			mailserver.login(destinataire,password)  									#Commande pour se connecter
			mailserver.sendmail(destinataire,destinataire, msg.as_string()) 			#Ouvrir, formulation et envois du mail 
			mailserver.quit()  
			print("Une/Des alerte(s) est/sont envoyee(s)") 								#Confirmation de l'envois du mail
			ConfirmMailSend = 1
		except:
			print("Impossible de se connecter a la boite mail (Identifiants non-valide)") 	
			ConfirmMailSend = 0
	else:
		Alerte = 0
		ConfirmMailSend = 2
	app.after(10, AffichageTkinter(TempsEN, visibilite, degres, humidite, degresMin, degresMax, pression, Temps, Vvent, direcVent, DistVisibilite, ville, ConnectNetwork, PresenceVent, Alerte, destinataire, password, ConfirmMailSend))

def Quitapp():
	app.quit()

#Affichage application
from Tkinter import *
app = Tk()
app.title("Station Meteo")
app.resizable(width=False, height=False)
app.geometry("650x450+500+250")

PhraseIntroVille = Label(app, text="Entrer le nom de la ville:",font=("Helvetica", 8)).place(x=64 ,y=10)
EntryVille=StringVar()
Ville = Entry(app, width=40, textvariable=EntryVille,justify=CENTER).place(x=210, y=10)

PhraseIntroMail = Label(app, text="Entrer votre e-mail:",font=("Helvetica", 8)).place(x=78 ,y=30)
EntryDestinataire=StringVar()
Destinataire = Entry(app, width=40, textvariable=EntryDestinataire,justify=CENTER).place(x=210, y=30)

PhraseIntroPassword = Label(app, text="Entrer votre mot de passe:",font=("Helvetica", 8)).place(x=58 ,y=50)
EntryPassword=StringVar()
Password = Entry(app, width=40, textvariable=EntryPassword,justify=CENTER, show='*').place(x=210, y=50)

Valide = Button(app, text="Enregistrer", width=20, height=2, command=RecupInfoMeteo).place(x=215, y=80)
Quit = Button(app, text="Quitter", width=25, height=2, command=Quitapp).place(x=195, y=320)



app.mainloop()
