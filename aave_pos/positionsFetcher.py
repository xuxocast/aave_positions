from ThreadWithReturn import ThreadWithReturnValue as twr
from web3 import Web3
import pandas as pd
import json

node_url = 'https://polygon-mainnet.g.alchemy.com/v2/9LBjNLAAJpJ-Nt4FBqtRjjEdFmyHA3Rq'
myaddr = '0xbF7c98f09E9439d873b0992E8233AC5BC094B783'
web3 = Web3(Web3.HTTPProvider(node_url))

#-------------------------------------------------------------------------------------------------
# Allows access to dictionary keys as attributes
class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self
#-------------------------------------------------------------------------------------------------
# ABIS
with open('abis/aave_oracle.json') as json_data:
    aave_oracle = json.load(json_data)
    
with open('abis/aave_data_provider.json') as json_data:
    aave_data_provider = json.load(json_data)
#-------------------------------------------------------------------------------------------------
# ERC20 Token Addresses
wmatic = '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270'
wbtc   = '0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6'
weth   = '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619'
link   = '0x53E0bca35eC356BD5ddDFebbD1Fc0fD03FaBad39'
usdcP  = '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'
usdcN  = '0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359' 

tokens = AttrDict()
tokens.update({'wmatic':wmatic,'weth':weth,'wbtc':wbtc,'link':link,'usdcP':usdcP,'usdcN':usdcN})

tokens_ctrs = AttrDict()
tokens_ctrs.update({wmatic:'wmatic',weth:'weth',wbtc:'wbtc',link:'link',usdcP:'usdcP',usdcN:'usdcN'})

decimals = AttrDict()
decimals.update({'wmatic':18,'weth':18,'wbtc':18,'link':18,'usdcP':6,'usdcN':6})


# Aave (Polygon) data providers
aave_oracle_addr = '0xb023e699F5a33916Ea823A16485e259257cA8Bd1'
aave_data_prov_addr = '0x69FA688f1Dc47d4B5d8029D5a35FB7a548310654'
ctr_aave_oracle    = web3.eth.contract(address=aave_oracle_addr,abi=aave_oracle)
ctr_aave_data_prov = web3.eth.contract(address=aave_data_prov_addr,abi=aave_data_provider)
#################################################################################################


def getPrice(tokenName):
    tokenContract = tokens.get(tokenName)
    pp = ctr_aave_oracle.functions.getAssetPrice(tokenContract,).call()
    return pp/10**8

def getBalance(tokenName, btcprice):
    aave_data_prov_keys = ['currentATokenBalance', 'currentStableDebt', 'currentVariableDebt', 
                            'principalStableDebt',  'scaledVariableDebt', 'stableBorrowRate', 
                            'liquidityRate', 'stableRateLastUpdated', 'usageAsCollateralEnabled',]
    tokenContract = tokens.get(tokenName)
    pp = ctr_aave_data_prov.functions.getUserReserveData(
                tokenContract,myaddr).call()
    r = {aave_data_prov_keys[i]:pp[i] for i in range(len(pp))}
    tokenDecimals = decimals.get(tokenName)

    bal  = r['currentATokenBalance'] / 10**tokenDecimals
    debt = r['currentVariableDebt'] / 10**8
    price = getPrice(tokenName)


    dd = {'balance':round(bal,4),'debt':round(debt,7),
    'usdBal':round(bal*price,4),'btcBal':round(bal*price/btcprice ,7),
    'usdDebt':round(debt*price,4), 'price':round(price,4)}

    return dd


def getAaveBalance(listTokenNames):
    rr = {}
    ths = []
    btcprice  = getPrice('wbtc')
    for tokenName in listTokenNames:
        th = twr(target=getBalance, args = (tokenName, btcprice,),)
        th.start()
        ths.append(th)
    r = {listTokenNames[i]:ths[i].join() for i in range(len(ths))}
    df = pd.DataFrame(r).T
    return df.sort_values('balance',ascending=False,)