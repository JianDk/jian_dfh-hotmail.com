import datetime
class ManageOrder:

    def __init__(self, **kwargs):

        self.API_VERSION = "2020-04"

        if kwargs['switch'] == 'DK':
            self.API_KEY = "f7bf71f3f3b7ce0a6f75863bdfccf53e"
            self.PASSWORD = "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"
            self.shop_url = "https://%s:%s@jian-xiong-wu.myshopify.com/admin/api/%s" % (self.API_KEY, self.PASSWORD, self.API_VERSION)
            self.databasePath = 'orderDBDK.db'

        if kwargs['switch'] == 'HK':
            self.API_KEY = "11d1233bd98782e8967a340918334686"
            self.PASSWORD = "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"
            self.shop_url = "https://%s:%s@alexanderystore.myshopify.com/admin/api/%s" % (self.API_KEY, self.PASSWORD, self.API_VERSION)
            self.databasePath = 'orderDBHK.db'
    
    def incomeStatus(self):
        '''
        get how much income is currently in HK and DK site for the current month. The currency is in DK.
        '''
        #Get current income in HK for this month
        self.__init__(switch = 'HK')
        currentMonth = datetime.datetime.now().month
        #Get the payouts from HK for this month
        
        print(currentMonth)
        


mo = ManageOrder(switch = 'HK')
mo.incomeStatus()

