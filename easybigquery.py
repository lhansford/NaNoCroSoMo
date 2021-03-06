import httplib2
from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials

class GoogleAPIFromServiceAccount(object):
	"""Stores API information for a Google service account."""

	def __init__(self, projectNumber, svcEmail, key):
		self.projectNumber = projectNumber
		self.serviceAccountEmail = svcEmail
		self.key = key
	# 
	# def readKey(self, keyPath):
	# 	"""Reads API private key stored at keyPath."""
	# 	try:
	# 		with open(keyPath, 'rb') as f:
	# 			key = f.read()
	# 		return key
	# 	except IOError as e:
	# 		print ("Invalid key file specified: %d") % e

class GoogleBigQuery(object):
	"""A basic Google BigQuery interface that lets you get results from arbitrary queries."""

	def __init__(self, api):
		if ( isinstance(api, GoogleAPIFromServiceAccount) ):
			self.api = api
			self.scope = "https://www.googleapis.com/auth/bigquery"
			self.service = None
			self.authenticateService()
		else:
			raise Exception("The API object given was not valid and is of type %s." % type(api))

	def authenticateService(self):
		if ( self.service == None ):
			credentials = SignedJwtAssertionCredentials(self.api.serviceAccountEmail, self.api.key, self.scope)
			httpObject = credentials.authorize(httplib2.Http())
			service = build('bigquery', 'v2', http=httpObject)
			self.service = service
		else:
			return False

	def query(self, sql):
		queryData = {'query': sql}
		queryRequest = self.service.jobs()
		queryResponse = queryRequest.query(projectId=self.api.projectNumber, body=queryData).execute()
		return queryResponse
