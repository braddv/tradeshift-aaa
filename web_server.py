from bottle import route, run, template, get, post, request
from mechanize import Browser
import requests
import time
import string

@get('/')
def create():
	return '''
	        <form action="/login" method="post">
		Email: <input name="email" type="text" />
		Company: <input name="company" type="text" />
		<input value="Create" type="submit" />
		</form> 
	'''

@post('/login')
def do_create():
	email = request.forms.get('email')
	company = request.forms.get('company')
	do_request(email,company)
	return "Done!"

@get('/done')
def done():
	return "Woot!"

def do_request(email,company):
	print(email)
	print('---')
	accountDetails = {"callbackURL":"http://localhost:8080", "twolegged":"true","email":email,"firstname":"Brad","lastname":"Voracek","title":"none","companyName":company,"street":"Lumbard St","buildingnumber":"123","locality":"US","zip":"94611","city":"San Francisco","state":"CA","recipient":"DK","country":"US","phone":"6613500794","fax":"","timezone":"GMT","tsRegnoLabel":"","tsRegnoValue":"","tsVATLabel":"","tsVATValue":"","gln":"","dkCVR":"","gbVAT":"","ieVAT":"","deSTN":"","deMWST":"","atSTN":"","atMWST":"","chMWST":""}
	requestHeaders = {"X-Tradeshift-ConsumerKey":"mbGvpE1ZfrghMZXEenjW","Accept":"text/html,application/xml","User-Agent":"python-request/1.2.0"}
	r = requests.get("http://localhost:8888/tradeshift-backend/rest/external/xsite/signup?callbackURL=%(callbackURL)s&twolegged=%(twolegged)s&email=%(email)s&firstname=%(firstname)s&lastname=%(lastname)s&title=%(title)s&companyName=%(companyName)s&street=%(street)s&buildingnumber=%(buildingnumber)s&locality=%(locality)s&zip=%(zip)s&city=%(city)s&state=%(state)s&recipient=%(recipient)s&country=%(country)s&phone=%(phone)s&fax=%(fax)s&timezone=%(timezone)s&tsRegnoLabel=%(tsRegnoLabel)s&tsRegnoValue=%(tsRegnoValue)s&tsVATLabel=%(tsVATLabel)s&tsVATValue=%(tsVATValue)s&gln=%(gln)s&dkCVR=%(dkCVR)s&gbVAT=%(gbVAT)s&ieVAT=%(ieVAT)s&deSTN=%(deSTN)s&deMWST=%(deMWST)s&atSTN=%(atSTN)s&atMWST=%(atMWST)s&chMWST=%(chMWST)s" % accountDetails, headers=requestHeaders)	
	browser = Browser()
	browser.set_handle_robots(False)
	browser.open(r.url)
	browser.select_form(nr=0)
	browser.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'), ('X-Tradeshift-ConsumerKey', 'mbGvpE1ZfrghMZXEenjW')]
	response = browser.submit()
	print(response.info())
	print(response.geturl())
	time.sleep(10)
	r = requests.get("http://localhost:8080/register/password?execution=e6s1&isLoginRegister=true&email=" + email)
	browser.open(r.url)
	browser.select_form(nr=0)
	response = browser.submit()
	print(response.info())
	print(response.geturl())
	time.sleep(30)
	import imaplib
	m = imaplib.IMAP4_SSL("imap.gmail.com")
	m.login("tradeshiftaaatest@gmail.com","shifthappens")
	m.select("INBOX")
	replace_string = '(TO "'+string.replace(email,'%2B','+')+'" SUBJECT "Tradeshift Password Reset")'
	print(replace_string)
	result,data = m.uid('search',None,replace_string)
	print(m.uid('fetch',data[0],'(RFC822)'))

run(host='localhost',port=8000)

