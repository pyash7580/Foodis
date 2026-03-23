import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = 'your_sendinblue_api_key_here'

try:
    api_instance = sib_api_v3_sdk.AccountApi(sib_api_v3_sdk.ApiClient(configuration))
    account = api_instance.get_account()
    print('SUCCESS! Key is VALID.')
    print('Email:', account.email)
    print('Plan Name:', account.plan[0].plan_type)
except ApiException as e:
    print('FAILED! Key is INVALID or email is unverified.')
    print('Reason:', e.reason)

