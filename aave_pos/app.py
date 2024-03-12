import positionsFetcher as pf
import json

'''
df = pf.getAaveBalance(['wmatic','wbtc',])
print(df.to_markdown(tablefmt='pretty', index=False),'\n')
totalBal = df.usdBal.sum() - df.usdDebt.sum()
print('Balance = ',round(totalBal,4),' USD')
mp = pf.getPrice('wmatic')
print('Matic b = ',round(totalBal/mp,4),' matic')

# import requests
'''

def lambda_handler(event, context):
    df = pf.getAaveBalance(['wmatic','wbtc',])
    totalBal = df.usdBal.sum() - df.usdDebt.sum()
    mp = pf.getPrice('wmatic')

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "successo",
            "Balance": round(totalBal,4),
            "Matic bal": round(totalBal/mp,4),
        }),
    }

if __name__ == "__main__":
    print(lambda_handler('',''))
