from bottle import route, run, template, get, post, request
from mechanize import Browser
import requests
import time
import string
import re
from lxml import etree
import uuid
import json

@get('/') 
def create():
	return '''
		<header>
		Awesome Account Automation App
		<link rel="stylesheet" href="http://localhost:8777/static/css/ts.css"/>
		<style>input{margin-bottom: 10px;}</style>
		</header>
	        <form action="/" method="post">
		Test gmail username: 
		<input name="email" type="text" class="t" />@gmail.com <br>
		Test gmail password: <input name="password" type="text" class="t" /> <br>
		Number of suppliers: <input name="number" type="text" class="t" /> <br>
		<input value="Create" type="submit" class="t" />
		</form> 
	'''

@post('/')
def do_create():
	emails = []
	companies = []
	email = request.forms.get('email')
	password = request.forms.get('password')
	number_suppliers = int(request.forms.get('number'))
	buyer_email = email+'%2Bbuyer@gmail.com'
	buyer_company = email + " buyer"
	emails.append(buyer_email)
	companies.append(buyer_company)
	for i in range(number_suppliers):
		supplier_email = email+'%2Bsupplier'+str(i)+'@gmail.com'
		supplier_company = email + " supplier " + str(i)
		emails.append(supplier_email)
		companies.append(supplier_company)
	for i in range(len(emails)):
		xsitesignup(emails[i],companies[i])
		time.sleep(1)
		reset_password(emails[i])
		time.sleep(1)
	time.sleep(20)
	uuids = activate_emails(emails,email,password)
	connect_accounts(uuids)
	return "Done!"

def xsitesignup(email,company):
	accountDetails = {"callbackURL":"http://localhost:8080", "twolegged":"true","email":email,"firstname":"Brad","lastname":"Voracek","title":"none","companyName":company,"street":"Lumbard St","buildingnumber":"123","locality":"US","zip":"94611","city":"San Francisco","state":"CA","recipient":"DK","country":"US","phone":"6613500794","fax":"","timezone":"GMT","tsRegnoLabel":"","tsRegnoValue":"","tsVATLabel":"","tsVATValue":"","gln":"","dkCVR":"","gbVAT":"","ieVAT":"","deSTN":"","deMWST":"","atSTN":"","atMWST":"","chMWST":""}
	requestHeaders = {"X-Tradeshift-ConsumerKey":"mbGvpE1ZfrghMZXEenjW","Accept":"text/html,application/xml","User-Agent":"python-request/1.2.0"}
	r = requests.get("http://localhost:8888/tradeshift-backend/rest/external/xsite/signup?callbackURL=%(callbackURL)s&twolegged=%(twolegged)s&email=%(email)s&firstname=%(firstname)s&lastname=%(lastname)s&title=%(title)s&companyName=%(companyName)s&street=%(street)s&buildingnumber=%(buildingnumber)s&locality=%(locality)s&zip=%(zip)s&city=%(city)s&state=%(state)s&recipient=%(recipient)s&country=%(country)s&phone=%(phone)s&fax=%(fax)s&timezone=%(timezone)s&tsRegnoLabel=%(tsRegnoLabel)s&tsRegnoValue=%(tsRegnoValue)s&tsVATLabel=%(tsVATLabel)s&tsVATValue=%(tsVATValue)s&gln=%(gln)s&dkCVR=%(dkCVR)s&gbVAT=%(gbVAT)s&ieVAT=%(ieVAT)s&deSTN=%(deSTN)s&deMWST=%(deMWST)s&atSTN=%(atSTN)s&atMWST=%(atMWST)s&chMWST=%(chMWST)s" % accountDetails, headers=requestHeaders)	
	browser.open(r.url)
	browser.select_form(nr=0)
	browser.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'), ('X-Tradeshift-ConsumerKey', 'mbGvpE1ZfrghMZXEenjW')]
	browser.submit()

def reset_password(email):
	r = requests.get("http://localhost:8080/register/password?execution=e6s1&isLoginRegister=true&email=" + email)
	browser.open(r.url)
	browser.select_form(nr=0)
	browser.submit()

def activate_emails(emails,email,password):
 	import imaplib
	m = imaplib.IMAP4_SSL("imap.gmail.com")
	m.login(email+"@gmail.com",password)
	uuids = []
	for email in emails:
		m.select("INBOX")
		replace_string = '(TO "'+string.replace(email,'%2B','+')+'" SUBJECT "Tradeshift Password Reset")'
		result,data = m.uid('search',None,replace_string)
		htmlbullshit = m.uid('fetch',data[0],'(RFC822)')[1][0][1]
		match = re.compile('(?<=href=").*?(?=")')
		activate = match.findall(htmlbullshit)[1]
		r = requests.get(activate)
		browser = Browser()
		browser.set_handle_robots(False)
		browser.open(r.url)
		match = re.compile('(?<=user=).*?(?=&)')
		uuid = match.findall(r.url)[0]
		uuids.append(uuid)
		browser.select_form(nr=0)
		browser["password"]=password
		browser.submit()
		browser.close()
	return uuids

def connect_accounts(uuids):
	tenantids = []
	for uuid in uuids:
		r = requests.get("http://localhost:8888/tradeshift-backend/rest/external/account/users/"+str(uuid))
		xml = string.replace(str(r.text),'\n','')
		root = etree.XML(xml)
		tenantid = root[1].text
		tenantids.append(tenantid)
	for tenant in tenantids[1:]:
		build_connection(tenant,tenantids[0])
		time.sleep(1)

def build_connection(supplierid,buyerid):
	generated_uuid = str(uuid.uuid4())
	connection = {"ConnectionType":"TradeshiftConnection","ConnectionId":generated_uuid,"CompanyAccountId":buyerid,"State":"REQUESTED"}
	requestHeaders = {"X-Tradeshift-TenantId":supplierid,"content-type":"application/json","User-Agent":"python-request/1.2.0"}
	connection = json.dumps(connection)
	r = requests.put("http://localhost:8888/tradeshift-backend/rest/external/network/connections/"+generated_uuid,data=connection,headers=requestHeaders)
	time.sleep(1)
	requestHeaders = {"X-Tradeshift-TenantId":buyerid,"content-type":"application/json","User-Agent":"python-request/1.2.0"}
	r = requests.post("http://localhost:8888/tradeshift-backend/rest/external/network/requests/"+generated_uuid+"/accept",headers=requestHeaders)

browser = Browser()
browser.set_handle_robots(False) 
run(host='localhost',port=8000)

