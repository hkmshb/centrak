import io
import os
from datetime import datetime
from django.conf import settings
from django.db import connections
from django.core.exceptions import ValidationError

from sqlalchemy import create_engine
import pandas as pd

from dolfin.data import XlSheet



def handle_uploaded_files(upl_obj):
    dtfolder = datetime.today().strftime("%Y%m%d")
    dir_root = os.path.join(settings.MEDIA_ROOT, dtfolder)
    if not os.path.exists(dir_root):
        os.makedirs(dir_root)
    
    dtname = datetime.today().strftime("%H%M%S")
    filename = "%s-%s" % (dtname, upl_obj.name)

    filepath = os.path.join(dir_root, filename)
    try:
        with open(filepath, 'wb+') as destination:
            for chunk in upl_obj.chunks():
                destination.write(chunk)
            destination.flush()
        return filepath
    except:
        return None


class IXHandlerBase:
    
    def __init__(self, file_path):
        self._file_path = file_path

    def validate_column_headings(self):
        headers = (self.headers or ('fake-@#$%^',))
        xlsheet = XlSheet(self._file_path, 'accounts')
        if not XlSheet.find_headers(xlsheet, headers):
            raise ValidationError("Expected columns not found.")


class AccountIXHandler(IXHandlerBase):
    headers = ('sn', 'acct_no', 'book_code', 'cust_name', 'service_addr', 'cust_mobile', 'meter_no', 'tariff')

    def load_from_excel(self):
        self.validate_column_headings()

        # read data into DataFrame
        df = pd.read_excel(self._file_path, 'accounts')
        df.rename(columns={'mobile':'phone'}, inplace=True)
        df['date_created'] = datetime.today().strftime("%Y-%m-%d")
        del df['sn']
        
        # TODO: compose this using settings entries ...
        engine = create_engine("postgresql://abdulhakeem:gai@localhost/CENTrak2") 
        df.to_sql('enum_account', engine, if_exists='append', index=False)
