def initialize(self):
        # Startup validation check for API keys
        import os
        if 'ZERODHA_API_KEY' not in os.environ or 'ZERODHA_API_SECRET' not in os.environ:
            raise EnvironmentError("API keys not found in environment variables.")
        # Proceed with connecting to the broker...
        self.connect_to_broker()