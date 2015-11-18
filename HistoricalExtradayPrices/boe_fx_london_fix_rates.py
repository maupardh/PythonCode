import pandas as pd
import datetime
import Utilities.assets
import Utilities.markets
import common_extraday_tools


def import_boe_london_fix_rates():

    fx_assets = Utilities.assets.get_assets()
    fx_assets['ID_BB_GLOBAL'] = fx_assets.index
    fx_assets = fx_assets[fx_assets['MARKET_SECTOR_DES'] == 'Curncy']
    fx_assets = fx_assets[fx_assets['SECURITY_TYP'] == 'CROSS']
    fx_assets = fx_assets[['ID_BB_GLOBAL', 'ID_BB_SEC_NUM_DES', 'MARKET_SECTOR_DES']]
    fx_assets = fx_assets[fx_assets['ID_BB_SEC_NUM_DES'].apply(lambda ccy_pair: len(ccy_pair) == 6)]
    fx_assets = fx_assets[fx_assets['ID_BB_SEC_NUM_DES'].apply(
        lambda ccy_pair: (ccy_pair[0:3] in Utilities.markets.HISTORIZED_FX_SPOTS or ccy_pair[0:3] == 'USD') and
                         (ccy_pair[3:] in Utilities.markets.HISTORIZED_FX_SPOTS or ccy_pair[3:] == 'USD'))]
    fx_assets.drop_duplicates(inplace=True)
    fx_assets.sort_values(by='ID_BB_SEC_NUM_DES', axis=0, ascending=True, inplace=True)
    ccy_pair_to_bb_id = dict(zip(fx_assets['ID_BB_SEC_NUM_DES'], fx_assets['ID_BB_GLOBAL']))
    boe_code_to_ccy_pair = {
        'XUDLADD': 'USDAUD',
        'XUDLB8KL': 'USDBRL',
        'XUDLCDD': 'USDCAD',
        'XUDLSFD': 'USDCHF',
        'XUDLBK73': 'USDCNY',
        'XUDLDKD': 'USDDKK',
        'XUDLERD': 'USDEUR',
        'XUDLGBD': 'USDGBP',
        'XUDLHDD': 'USDHKD',
        'XUDLBK65': 'USDILS',
        'XUDLBK64': 'USDINR',
        'XUDLBK66': 'USDMYR',
        'XUDLJYD': 'USDJPY',
        'XUDLBK74': 'USDKRW',
        'XUDLNKD': 'USDNOK',
        'XUDLBK49': 'USDPLN',
        'XUDLBK69': 'USDRUB',
        'XUDLSRD': 'USDSAR',
        'XUDLSKD': 'USDSEK',
        'XUDLSGD': 'USDSGD',
        'XUDLBK75': 'USDTRY',
        'XUDLTWD': 'USDTWD',
        'XUDLZRD': 'USDZAR',
        'XUDLNDD': 'USDNZD'
    }

    path_to_boe_csv = ''  # FILL
    fx_prices = pd.read_csv(path_to_boe_csv)
    fx_prices.index = fx_prices['DATE'].apply(
        lambda d: datetime.datetime.strptime(d, "%Y-%m-%d").date())
    fx_prices.drop('DATE', axis=1, inplace=True)
    fx_prices = fx_prices.applymap(float)
    fx_prices.rename(columns=boe_code_to_ccy_pair, inplace=True)
    fx_prices_flipped = fx_prices.rename(columns=lambda t: t[3:6]+t[0:3])
    fx_prices_flipped = fx_prices_flipped.applymap(lambda x: 1/x if x > 0 else 0)

    merged_fx_prices = pd.concat([fx_prices, fx_prices_flipped])
    merged_fx_prices.rename(columns=ccy_pair_to_bb_id, inplace=True)
    for (cur_date, cur_row) in merged_fx_prices.to_dict(orient='index').iteritems():
        cur_prices = pd.from_dict(cur_row, orient='index')
        common_extraday_tools.write_extraday_prices_table_for_single_day(cur_prices, cur_date)

import_boe_london_fix_rates()
