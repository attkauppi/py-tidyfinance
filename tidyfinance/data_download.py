"""Data download and retrieval module for tidyfinance."""

import pandas as pd
import numpy as np
import requests
import os
import pandas_datareader as pdr
from sqlalchemy import text
from ._internal import (_validate_dates,
                        _return_datetime,
                        _transfrom_to_snake_case,
                        _assign_exchange,
                        _assign_industry
                        )
from .utilities import (get_random_user_agent,
                        get_wrds_connection,
                        disconnect_connection,
                        process_trace_data
                        )


def create_wrds_dummy_database(
    path: str,
    url: str = ("https://github.com/tidy-finance/website/raw/main/blog/"
                "tidy-finance-dummy-data/data/tidy_finance.sqlite")
) -> None:
    """
    Download the WRDS dummy database from the Tidy Finance GitHub repository.

    It saves it to the specified path. If the file already exists,
    the user is prompted before it is replaced.

    Parameters
    ----------
        path (str): The file path where the SQLite database should be saved.
        url (str, optional): The URL where the SQLite database is stored.

    Returns
    -------
        None: Side effect - downloads a file to the specified path.
    """
    if not path:
        raise ValueError("Please provide a file path for the SQLite database. "
                         "We recommend 'data/tidy_finance.sqlite'.")

    if os.path.exists(path):
        response = input("The database file already exists at this path. Do "
                         "you want to replace it? (Y/n): ")
        if response.strip().lower() != "y":
            print("Operation aborted by the user.")
            return

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                print(chunk)
                file.write(chunk)
        print(f"Downloaded WRDS dummy database to {path}.")
    except requests.RequestException as e:
        print(f"Error downloading the WRDS dummy database: {e}")


def download_data(
    data_set: str,
    start_date: str = None,
    end_date: str = None,
    **kwargs
) -> pd.DataFrame:
    """
    Download and process data based on the specified type.

    Parameters
    ----------
    data_set : str
        The type of dataset to download, indicating either factor data or
        macroeconomic predictors  (e.g., Fama-French factors, Global Q factors,
                                   or macro predictors).
    start_date : str, optional
        The start date for filtering the data, in "YYYY-MM-DD" format.
    end_date : str, optional
        The end date for filtering the data, in "YYYY-MM-DD" format.
    **kwargs : dict
        Additional arguments passed to specific download functions depending
        on the `type`.

    Returns
    -------
    pd.DataFrame
        A DataFrame with processed data, including dates and relevant financial
        metrics, filtered by the specified date range.
    """
    if "factors" in data_set:
        processed_data = download_data_factors(
            data_set, start_date, end_date, **kwargs
            )
    elif "macro_predictors" in data_set:
        processed_data = download_data_macro_predictors(
            data_set, start_date, end_date, **kwargs
            )
    elif "wrds" in data_set:
        processed_data = download_data_wrds(
            data_set, start_date, end_date, **kwargs
            )
    elif "constituents" in data_set:
        processed_data = download_data_constituents(**kwargs)
    elif "fred" in data_set:
        processed_data = download_data_fred(
            start_date=start_date, end_date=end_date, **kwargs
            )
    elif "stock_prices" in data_set:
        processed_data = download_data_stock_prices(
            start_date=start_date, end_date=end_date, **kwargs
            )
    elif "osap" in data_set:
        processed_data = download_data_osap(start_date, end_date, **kwargs)
    else:
        raise ValueError("Unsupported data type.")
    return processed_data


def download_data_factors(
    data_set: str,
    start_date: str = None,
    end_date: str = None,
    **kwargs
) -> pd.DataFrame:
    """
    Download and process factor data for the specified type and date range.

    Parameters
    ----------
    data_set : str
        The type of dataset to download, indicating factor model and frequency.
    start_date : str, optional
        The start date for filtering the data, in "YYYY-MM-DD" format.
    end_date : str, optional
        The end date for filtering the data, in "YYYY-MM-DD" format.

    Returns
    -------
    pd.DataFrame
        A DataFrame with processed factor data, including dates,
        risk-free rates, market excess returns, and other factors,
        filtered by the specified date range.
    """
    if "factors_ff" in data_set:
        return download_data_factors_ff(data_set, start_date, end_date)
    elif "factors_q" in data_set:
        return download_data_factors_q(data_set, start_date, end_date)
    else:
        raise ValueError("Unsupported factor data type.")


def download_data_factors_ff(
    data_set: str,
    start_date: str = None,
    end_date: str = None
) -> pd.DataFrame:
    """Download and process Fama-French factor data."""
    start_date, end_date = _validate_dates(start_date, end_date)
    all_data_sets = pdr.famafrench.get_available_datasets()
    if data_set in all_data_sets:
        try:
            raw_data = (pdr.famafrench.FamaFrenchReader(
                data_set, start=start_date, end=end_date).read()[0]
                .div(100)
                .reset_index()
                .rename(columns=lambda x:
                        x.lower()
                        .replace("-rf", "_excess")
                        .replace("rf", "risk_free")
                        )
                .assign(date=lambda x: _return_datetime(x['date']))
                .apply(lambda x: x.replace([-99.99, -999], pd.NA)
                       if x.name != 'date' else x
                       )
                )
            raw_data = raw_data[
                ["date"] + [col for col in raw_data.columns if col != "date"]
                ].reset_index(drop=True)
            return raw_data
        except ValueError:
            raise ValueError("Unsupported factor data type.")
    else:
        raise ValueError("Returning an empty data set due to download failure")
        print(f"{data_set} is not in list of available data sets. "
              " Returns empty DataFrame. Choose a dataset from:")
        print("")
        print(all_data_sets)
        return pd.DataFrame()


def download_data_factors_q(
    data_set: str,
    start_date: str = None,
    end_date: str = None,
    url: str = "https://global-q.org/uploads/1/2/2/6/122679606/"
) -> pd.DataFrame:
    """
    Download and process Global Q factor data.

    Parameters
    ----------
    data_set : str
        The type of dataset to download (e.g., "factors_q5_daily",
                                         "factors_q5_monthly").
    start_date : str, optional
        The start date for filtering the data, in "YYYY-MM-DD" format.
    end_date : str, optional
        The end date for filtering the data, in "YYYY-MM-DD" format.
    url : str, optional
        The base URL from which to download the dataset files.

    Returns
    -------
    pd.DataFrame
        A DataFrame with processed factor data, including the date,
        risk-free rate, market excess return, and other factors.
    """
    start_date, end_date = _validate_dates(start_date, end_date)
    ref_year = pd.Timestamp.today().year - 1
    all_data_sets = [f"q5_factors_daily_{ref_year}",
                     f"q5_factors_weekly_{ref_year}",
                     f"q5_factors_weekly_w2w_{ref_year}",
                     f"q5_factors_monthly_{ref_year}",
                     f"q5_factors_quarterly_{ref_year}",
                     f"q5_factors_annual_{ref_year}"
                     ]
    if data_set in all_data_sets:
        raw_data = (pd.read_csv(f"{url}{data_set}.csv")
                    .rename(columns=lambda x: x.lower().replace("r_", ""))
                    .rename(columns={"f": "risk_free", "mkt": "mkt_excess"})
                    )
        if "monthly" in data_set:
            raw_data = (raw_data.assign(date=lambda x: pd.to_datetime(
                x["year"].astype(str) + "-" + x["month"].astype(str)+"-01")
                )
                .drop(columns=["year", "month"])
                )
        if "annual" in data_set:
            raw_data = (raw_data.assign(date=lambda x: pd.to_datetime(
                x["year"].astype(str) + "-01-01")
                )
                .drop(columns=["year"])
                )
        raw_data = (raw_data
                    .assign(date=lambda x: pd.to_datetime(x["date"]))
                    .apply(lambda x: x.div(100) if x.name != "date" else x)
                    )
        if start_date and end_date:
            raw_data = raw_data.query('@start_date <= date <= @end_date')
        raw_data = raw_data[
            ["date"] + [col for col in raw_data.columns if col != "date"]
            ].reset_index(drop=True)
        return raw_data
    else:
        raise ValueError("Returning an empty data set due to download "
                         "failure.")
        print(f"{data_set} might not be in list of available data sets: "
              " Also check the provided URL. Choose a dataset from:")
        print("")
        print(all_data_sets)
        return pd.DataFrame()


def download_data_macro_predictors(
    data_set: str,
    start_date: str = None,
    end_date: str = None,
    sheet_id: str = "1bM7vCWd3WOt95Sf9qjLPZjoiafgF_8EG"
) -> pd.DataFrame:
    """
    Download and process macroeconomic predictor data.

    Parameters
    ----------
    data_set : str
        The type of dataset to download ("Monthly", "Quarterly", "Annual")
    start_date : str, optional
        The start date for filtering the data, in "YYYY-MM-DD" format.
    end_date : str, optional
        The end date for filtering the data, in "YYYY-MM-DD" format.
    sheet_id : str, optional
        The Google Sheets ID from which to download the dataset.

    Returns
    -------
    pd.DataFrame
        A DataFrame with processed data, including financial metrics, filtered
        by the specified date range.
    """
    start_date, end_date = _validate_dates(start_date, end_date)

    if data_set in ["Monthly", "Quarterly", "Annual"]:
        try:
            macro_sheet_url = ("https://docs.google.com/spreadsheets/d/"
                               f"{sheet_id}/gviz/tq?tqx=out:csv&sheet="
                               f"{data_set}"
                               )
            raw_data = pd.read_csv(macro_sheet_url)
        except Exception:
            print("Expected an empty DataFrame due to download failure.")
            return pd.DataFrame()
    else:
        raise ValueError("Unsupported macro predictor type.")
        return pd.DataFrame()

    if data_set == "Monthly":
        raw_data = (raw_data
                    .assign(date=lambda x: pd.to_datetime(x["yyyymm"],
                                                          format="%Y%m")
                            )
                    .drop(columns=['yyyymm'])
                    )
    if data_set == "Quarterly":
        raw_data = (raw_data
                    .assign(date=lambda x: pd.to_datetime(
                        x["yyyyq"].astype(str).str[:4]
                        + "-" + (x["yyyyq"].astype(str).str[4].astype(int)
                                 * 3 - 2).astype(str)
                        + "-01")
                        )
                    .drop(columns=['yyyyq'])
                    )
    if data_set == "Annual":
        raw_data = (raw_data
                    .assign(date=lambda x:
                            pd.to_datetime(x["yyyy"].astype(str) + "-01-01")
                            )
                    .drop(columns=['yyyy'])
                    )

    raw_data = raw_data.apply(
        lambda x: pd.to_numeric(x.astype(str).str.replace(",", ""),
                                errors='coerce') if x.dtype == "object" else x)
    raw_data = raw_data.assign(
        IndexDiv=lambda df: df["Index"] + df["D12"],
        logret=lambda df: df["IndexDiv"].apply(
            lambda x: np.nan if pd.isna(x) else np.log(x)
            ).diff(),
        rp_div=lambda df: df["logret"].shift(-1) - df["Rfree"],
        log_d12=lambda df: df["D12"].apply(
            lambda x: np.nan if pd.isna(x) else np.log(x)
            ),
        log_e12=lambda df: df["E12"].apply(
            lambda x: np.nan if pd.isna(x) else np.log(x)),
        dp=lambda df: df["log_d12"] - df["Index"].apply(
            lambda x: np.nan if pd.isna(x) else np.log(x)),
        dy=lambda df: df["log_d12"] - df["Index"].shift(1).apply(
            lambda x: np.nan if pd.isna(x) else np.log(x)
            ),
        ep=lambda df: df["log_e12"] - df["Index"].apply(
            lambda x: np.nan if pd.isna(x) else np.log(x)
            ),
        de=lambda df: df["log_d12"] - df["log_e12"],
        tms=lambda df: df["lty"] - df["tbl"],
        dfy=lambda df: df["BAA"] - df["AAA"]
    )

    raw_data = raw_data[[
        "date", "rp_div", "dp", "dy", "ep", "de", "svar", "b/m", "ntis",
        "tbl", "lty", "ltr", "tms", "dfy", "infl"
        ]]
    raw_data = (raw_data
                .rename(columns={col: col.replace("/", "")
                                 for col in raw_data.columns}
                        )
                .dropna()
                )

    if start_date and end_date:
        raw_data = raw_data.query('@start_date <= date <= @end_date')

    return raw_data


def download_data_fred(
    series: str | list,
    start_date: str = None,
    end_date: str = None,
) -> pd.DataFrame:
    """
    Download and process data from FRED.

    Parameters
    ----------
    series : str or list
        A list of FRED series IDs to download.
    start_date : str, optional
        The start date for filtering the data, in "YYYY-MM-DD" format.
    end_date : str, optional
        The end date for filtering the data, in "YYYY-MM-DD" format.

    Returns
    -------
    pd.DataFrame
        A DataFrame with processed data, including the date, value,
        and series ID, filtered by the specified date range.
    """
    if isinstance(series, str):
        series = [series]

    start_date, end_date = _validate_dates(start_date, end_date)
    fred_data = []

    for s in series:
        url = f"https://fred.stlouisfed.org/series/{s}/downloaddata/{s}.csv"
        headers = {"User-Agent": get_random_user_agent()}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            raw_data = (pd.read_csv(pd.io.common.StringIO(response.text))
                        .rename(columns=lambda x: x.lower())
                        .assign(date=lambda x: pd.to_datetime(x["date"]),
                                value=lambda x: pd.to_numeric(x["value"],
                                                              errors='coerce'),
                                series=s
                                )
                        )

            fred_data.append(raw_data)
        except requests.RequestException as e:
            print(f"Failed to retrieve data for series {s}: {e}")
            fred_data.append(pd.DataFrame(columns=["date", "value", "series"]))

    fred_data = pd.concat(fred_data, ignore_index=True)

    if start_date and end_date:
        fred_data = fred_data.query('@start_date <= date <= @end_date')

    return fred_data


def download_data_stock_prices(
    symbols: str | list,
    start_date: str = None,
    end_date: str = None,
) -> pd.DataFrame:
    """
    Download historical stock data from Yahoo Finance.

    Parameters
    ----------
    symbols : list
        A list of stock symbols to download data for.
        At least one symbol must be provided.
    start_date : str, optional
        Start date in "YYYY-MM-DD" format. Defaults to "2000-01-01".
    end_date : str, optional
        End date in "YYYY-MM-DD" format. Defaults to today's date.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing columns: symbol, date, volume, open, low,
        high, close, adjusted_close.
    """
    if isinstance(symbols, str):
        symbols = [symbols]
    elif not isinstance(symbols, list) or not all(isinstance(sym, str)
                                                  for sym in symbols):
        raise ValueError("symbols must be a list of stock symbols (strings).")

    start_date, end_date = _validate_dates(start_date, end_date)

    if start_date is None:
        start_date = pd.Timestamp.today() - pd.DateOffset(years=2)
    if end_date is None:
        end_date = pd.Timestamp.today()

    start_timestamp = int(pd.Timestamp(start_date).timestamp())
    end_timestamp = int(pd.Timestamp(end_date).timestamp())

    all_data = []

    for symbol in symbols:
        url = (f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}"
               f"?period1={start_timestamp}&period2={end_timestamp}"
               "&interval=1d"
               )

        headers = {"User-Agent": get_random_user_agent()}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            raw_data = response.json().get("chart", {}).get("result", [])

            if (not raw_data) or ('timestamp' not in raw_data[0]):
                print(f"Warning: No data found for {symbol}.")
                continue

            timestamps = raw_data[0]["timestamp"]
            indicators = raw_data[0]["indicators"]["quote"][0]
            adjusted_close = (raw_data[0]["indicators"]["adjclose"][0]
                              ["adjclose"]
                              )

            processed_data_symbol = (
                pd.DataFrame()
                .assign(date=pd.to_datetime(pd.to_datetime(timestamps,
                                                           utc=True,
                                                           unit="s").date),
                        symbol=symbol,
                        volume=indicators.get("volume"),
                        open=indicators.get("open"),
                        low=indicators.get("low"),
                        high=indicators.get("high"),
                        close=indicators.get("close"),
                        adjusted_close=adjusted_close
                        )
                .dropna()
                )

            all_data.append(processed_data_symbol)

        else:
            print(f"Failed to retrieve data for {symbol} (Status code: "
                  f"{response.status_code})")

    all_data = pd.concat(all_data,
                         ignore_index=True) if all_data else pd.DataFrame()
    return all_data


def download_data_osap(
    start_date: str = None,
    end_date: str = None,
    sheet_id: str = "1JyhcF5PRKHcputlioxlu5j5GyLo4JYyY"
) -> pd.DataFrame:
    """
    Download and process Open Source Asset Pricing (OSAP) data.

    Parameters
    ----------
    start_date : str, optional
        Start date in "YYYY-MM-DD" format. If None, full dataset is returned.
    end_date : str, optional
        End date in "YYYY-MM-DD" format. If None, full dataset is returned.
    sheet_id : str, optional
        Google Sheet ID from which to download the dataset.
        Default is "1JyhcF5PRKHcputlioxlu5j5GyLo4JYyY".

    Returns
    -------
    pd.DataFrame
        Processed dataset with snake_case column names,
        filtered by date range if provided.
    """
    start_date, end_date = _validate_dates(start_date, end_date)

    # Google Drive direct download link
    url = f"https://drive.google.com/uc?export=download&id={sheet_id}"

    try:
        raw_data = pd.read_csv(url)
    except Exception:
        print("Returning an empty dataset due to download failure.")
        return pd.DataFrame()

    if raw_data.empty:
        print("Returning an empty dataset due to download failure.")
        return raw_data

    # Convert date column to datetime format
    if "date" in raw_data.columns:
        raw_data["date"] = pd.to_datetime(raw_data["date"], errors="coerce")

    # Convert column names to snake_case
    raw_data.columns = [_transfrom_to_snake_case(col)
                        for col in raw_data.columns]

    # Filter data based on date range
    if start_date and end_date:
        raw_data = raw_data.query('@start_date <= date <= @end_date')

    return raw_data


def download_data_wrds(
    data_type: str,
    start_date: str = None,
    end_date: str = None,
    **kwargs
) -> dict:
    """
    Download data from WRDS based on the specified type.

    Parameters
    ----------
    data_type (str): Type of data to download
        (e.g., "wrds_crsp", "wrds_compustat").
    start_date (str, optional): Start date in "YYYY-MM-DD" format.
    end_date (str, optional): End date in "YYYY-MM-DD" format.
    **kwargs: Additional parameters specific to the dataset type.

    Returns
    -------
        dict: A dictionary representing the downloaded data.
    """
    if "wrds_crsp" in data_type:
        return download_data_wrds_crsp(
            data_type, start_date, end_date, **kwargs
            )
    elif "wrds_compustat" in data_type:
        return download_data_wrds_compustat(
            data_type, start_date, end_date, **kwargs
            )
    elif "wrds_ccm_links" in data_type:
        return download_data_wrds_ccm_links(**kwargs)
    elif "wrds_fisd" in data_type:
        return download_data_wrds_fisd(**kwargs)
    elif "wrds_trace_enhanced" in data_type:
        return download_data_wrds_trace_enhanced(
            start_date, end_date, **kwargs
            )
    else:
        raise ValueError("Unsupported data type.")
    return {}


def download_data_wrds_crsp(
    dataset_type: str = "crsp_monthly",
    start_date: str = None,
    end_date: str = None,
    batch_size: int = 500,
    version: str = "v2",
    additional_columns: list = None
) -> pd.DataFrame:
    """
    Download stock return data from WRDS CRSP.

    Parameters
    ----------
        type (str): The type of CRSP data to download. Expected values:
            "crsp_monthly" or "crsp_daily".
        start_date (str or None): Start date in "YYYY-MM-DD" format (optional).
        end_date (str or None): End date in "YYYY-MM-DD" format (optional).
        batch_size (int): The batch size for processing daily data
            (default: 500).
        version (str): CRSP version to use ("v2" for updated, "v1" for legacy).
        additional_columns (list or None): List of additional column names
            to retrieve (optional).

    Returns
    -------
        pandas.DataFrame: A DataFrame containing CRSP stock return data,
            adjusted for delistings.
    """
    start_date, end_date = _validate_dates(start_date, end_date)

    # Validate batch_size
    batch_size = int(batch_size)
    if batch_size <= 0:
        raise ValueError("batch_size must be an integer larger than 0.")

    # Validate version
    if version not in ["v1", "v2"]:
        raise ValueError("version must be 'v1' or 'v2'.")

    # Connect to WRDS
    wrds_connection = get_wrds_connection()
    additional_columns = (", ".join(additional_columns)
                          if additional_columns else ""
                          )

    crsp_data = pd.DataFrame()
    if "crsp_monthly" in dataset_type:
        if version == "v1":
            pass
        if version == "v2":

            crsp_query = (
                f"""
                SELECT msf.permno, date_trunc('month', msf.mthcaldt)::date
                    AS date, msf.mthret AS ret, msf.shrout, msf.mthprc
                    AS altprc, ssih.primaryexch, ssih.siccd
                    {", " + additional_columns if additional_columns else ""}
                FROM crsp.msf_v2 AS msf
                INNER JOIN crsp.stksecurityinfohist AS ssih
                ON msf.permno = ssih.permno AND
                    ssih.secinfostartdt <= msf.mthcaldt AND
                    msf.mthcaldt <= ssih.secinfoenddt
                WHERE msf.mthcaldt BETWEEN '{start_date}' AND '{end_date}'
                AND ssih.sharetype = 'NS'
                AND ssih.securitytype = 'EQTY'
                AND ssih.securitysubtype = 'COM'
                AND ssih.usincflg = 'Y'
                AND ssih.issuertype in ('ACOR', 'CORP')
                AND ssih.primaryexch in ('N', 'A', 'Q')
                AND ssih.conditionaltype in ('RW', 'NW')
                AND ssih.tradingstatusflg = 'A'
                """)

            crsp_monthly = (
                pd.read_sql_query(
                    sql=crsp_query,
                    con=wrds_connection,
                    dtype={"permno": int, "siccd": int},
                    parse_dates={"date"}
                    )
                .assign(shrout=lambda x: x["shrout"]*1000)
                .assign(mktcap=lambda x: x["shrout"]*x["altprc"]/1000000)
                .assign(mktcap=lambda x: x["mktcap"].replace(0, np.nan))
                )

            mktcap_lag = (
                crsp_monthly
                .assign(date=lambda x: x["date"]+pd.DateOffset(months=1),
                        mktcap_lag=lambda x: x["mktcap"]
                        )
                .get(["permno", "date", "mktcap_lag"])
                )

            crsp_monthly = (
                crsp_monthly
                .merge(mktcap_lag, how="left", on=["permno", "date"])
                .assign(exchange=lambda x:
                        x["primaryexch"].apply(_assign_exchange),
                        industry=lambda x: x["siccd"].apply(_assign_industry)
                        )
                )
            factors_ff3_monthly = download_data_factors_ff(
                'F-F_Research_Data_Factors')

            crsp_monthly = (
                crsp_monthly
                .merge(factors_ff3_monthly, how="left", on="date")
                .assign(ret_excess=lambda x: x["ret"]-x["rf"])
                .assign(ret_excess=lambda x: x["ret_excess"].clip(lower=-1))
                .drop(columns=["rf"])
                .dropna(subset=["ret_excess", "mktcap", "mktcap_lag"])
                )
            return crsp_monthly
    elif "crsp_daily" in dataset_type:
        if version == "v1":
            pass
        if version == "v2":

            permnos = pd.read_sql(
                sql="SELECT DISTINCT permno FROM crsp.stksecurityinfohist",
                con=wrds_connection,
                dtype={"permno": int}
                )
            permnos = list(permnos["permno"].astype(str))
            batches = np.ceil(len(permnos)/batch_size).astype(int)

            for j in range(1, batches+1):
                permno_batch = permnos[((j-1)*batch_size):(min(j*batch_size,
                                                               len(permnos)))
                                       ]
                permno_batch_formatted = (", ".join(f"'{permno}'"
                                                    for permno in permno_batch)
                                          )
                permno_string = f"({permno_batch_formatted})"

                crsp_daily_sub_query = (
                    f"""
                    SELECT dsf.permno, dlycaldt AS date, dlyret AS ret
                        {", " + additional_columns if additional_columns
                         else ""}
                    FROM crsp.dsf_v2 AS dsf
                    INNER JOIN crsp.stksecurityinfohist AS ssih
                    ON dsf.permno = ssih.permno AND
                        ssih.secinfostartdt <= dsf.dlycaldt AND
                        dsf.dlycaldt <= ssih.secinfoenddt
                    WHERE dsf.permno IN {permno_string}
                    AND dlycaldt BETWEEN '{start_date}' AND '{end_date}'
                    AND ssih.sharetype = 'NS'
                    AND ssih.securitytype = 'EQTY'
                    AND ssih.securitysubtype = 'COM'
                    AND ssih.usincflg = 'Y'
                    AND ssih.issuertype in ('ACOR', 'CORP')
                    AND ssih.primaryexch in ('N', 'A', 'Q')
                    AND ssih.conditionaltype in ('RW', 'NW')
                    AND ssih.tradingstatusflg = 'A'
                    """)

                crsp_daily_sub = (pd.read_sql_query(
                    sql=crsp_daily_sub_query,
                    con=wrds_connection,
                    dtype={"permno": int},
                    parse_dates={"date"}
                    )
                    .dropna()
                    )

                if not crsp_daily_sub.empty:

                    factors_ff3_daily = download_data_factors_ff(
                        'F-F_Research_Data_Factors_Daily')

                    crsp_daily_sub = (
                        crsp_daily_sub
                        .merge(factors_ff3_daily[["date", "rf"]],
                               on="date",
                               how="left")
                        .assign(ret_excess=lambda x:
                                ((x["ret"] - x["rf"]).clip(lower=-1))
                                )
                        .get(["permno", "date", "ret_excess"])
                        )

                print(f"Batch {j} out of {batches} done "
                      "({(j/batches)*100:.2f}%)\n")

                crsp_data = pd.concat([crsp_data, crsp_daily_sub])
            return crsp_data
    else:
        raise ValueError("Invalid type specified. Use 'crsp_monthly' "
                         "or 'crsp_daily'.")


def download_data_wrds_ccm_links(
    linktype: list[str] = ["LU", "LC"],
    linkprim: list[str] = ["P", "C"]
) -> pd.DataFrame:
    """
    Download data from the WRDS CRSP/Compustat Merged (CCM) links database.

    Parameters
    ----------
        linktype (list): A list of strings indicating the types of links to
        download. Default is ["LU", "LC"].
        linkprim (list): A list of strings indicating the primacy of the links.
        Default is ["P", "C"].

    Returns
    -------
        pd.DataFrame: A DataFrame containing columns:
            - `permno` (int): CRSP permanent number.
            - `gvkey` (str): Global company key.
            - `linkdt`: Start date of the link.
            - `linkenddt`: End date of the link
            (missing values replaced with today's date).
    """
    conn = get_wrds_connection()

    query = f"""
        SELECT lpermno AS permno, gvkey, linkdt, linkenddt
        FROM crsp.ccmxpf_lnkhist
        WHERE linktype IN ({','.join(f"'{lt}'" for lt in linktype)})
        AND linkprim IN ({','.join(f"'{lp}'" for lp in linkprim)})
    """

    ccm_links = pd.read_sql(query, conn)

    # Replace missing linkenddt with today's date
    ccm_links['linkenddt'] = (ccm_links['linkenddt']
                              .fillna(pd.Timestamp.today())
                              )

    disconnect_connection(conn)

    return ccm_links


def download_data_wrds_compustat(
    dataset_type: str = "compustat_quarterly",
    start_date: str = None,
    end_date: str = None,
    additional_columns: list = None
) -> pd.DataFrame:
    """
    Download financial data from WRDS Compustat.

    Parameters
    ----------
        type (str): Type of financial data to download. Expected values:
            "compustat_annual" or "compustat_quarterly".
        start_date (str or None): Start date in "YYYY-MM-DD" format (optional).
        end_date (str or None): End date in "YYYY-MM-DD" format (optional).
        additional_columns (list or None): A list of additional column names
        to retrieve (optional).

    Returns
    -------
        pandas.DataFrame: A DataFrame containing financial data for the
            specified period, including computed variables such as book equity
            (be), operating profitability (op), and investment (inv)
            for annual data.
    """
    start_date, end_date = _validate_dates(start_date, end_date)

    if dataset_type not in ["compustat_annual", "compustat_quarterly"]:
        raise ValueError("Invalid type specified. Use 'compustat_annual' or "
                         "'compustat_quarterly'.")

    # Connect to WRDS
    wrds_connection = get_wrds_connection()
    additional_columns = (", ".join(additional_columns)
                          if additional_columns else ""
                          )

    if "compustat_annual" in dataset_type:

        query = text(f"""
            SELECT gvkey, datadate, seq, ceq, at, lt, txditc, txdb, itcb,
                pstkrv, pstkl, pstk, capx, oancf, sale, cogs, xint, xsga
                {", " + additional_columns if additional_columns else ""}
            FROM comp.funda
            WHERE indfmt = 'INDL' AND datafmt = 'STD' AND consol = 'C'
            AND datadate BETWEEN '{start_date}' AND '{end_date}'
        """)

        compustat = pd.read_sql(query, wrds_connection)
        wrds_connection.dispose()

        # Compute Book Equity (be)
        compustat = (
            compustat
            .assign(
                be=lambda x:
                (x["seq"].combine_first(x["ceq"] + x["pstk"])
                 .combine_first(x["at"]-x["lt"]) +
                 x["txditc"].combine_first(x["txdb"]+x["itcb"]).fillna(0) -
                 x["pstkrv"].combine_first(x["pstkl"])
                 .combine_first(x["pstk"]).fillna(0))
                )
            .assign(be=lambda x: x["be"]
                    .apply(lambda y: np.nan if y <= 0 else y)
                    )
            .assign(op=lambda x:
                    ((x["sale"]-x["cogs"].fillna(0) - x["xsga"].fillna(0)
                      - x["xint"].fillna(0))/x["be"])
                    )
            )
        # Compute Operating Profitability (op)
        compustat = compustat.assign(
            op=lambda df: (df["sale"] - df[["cogs", "xsga", "xint"]]
                           .fillna(0).sum(axis=1)) / df["be"]
        )
        # Keep the latest report per company per year
        compustat = (
            compustat
            .assign(year=lambda x: pd.DatetimeIndex(x["datadate"]).year)
            .sort_values("datadate")
            .groupby(["gvkey", "year"])
            .tail(1)
            .reset_index()
            )
        # Compute Investment (inv)
        compustat_lag = (
            compustat
            .get(["gvkey", "year", "at"])
            .assign(year=lambda x: x["year"]+1)
            .rename(columns={"at": "at_lag"})
            )

        compustat = (
            compustat
            .merge(compustat_lag, how="left", on=["gvkey", "year"])
            .assign(inv=lambda x: x["at"]/x["at_lag"]-1)
            .assign(inv=lambda x: np.where(x["at_lag"] <= 0, np.nan, x["inv"]))
            )

        processed_data = compustat.drop(columns=["year", "at_lag"])

    elif "compustat_quarterly" in dataset_type:
        query = text(f"""
            SELECT gvkey, datadate, rdq, fqtr, fyearq, atq, ceqq
                {", " + additional_columns if additional_columns else ""}
            FROM comp.fundq
            WHERE indfmt = 'INDL' AND datafmt = 'STD' AND consol = 'C'
            AND datadate BETWEEN '{start_date}' AND '{end_date}'
        """)

        compustat = pd.read_sql(query, wrds_connection)
        wrds_connection.dispose()

        # Ensure necessary columns are not missing
        compustat = (compustat
                     .dropna(subset=["gvkey", "datadate", "fyearq", "fqtr"])
                     .assign(date=lambda df:
                             pd.to_datetime(df["datadate"])
                             .dt.to_period("M").dt.start_time
                             )
                     .sort_values("datadate")
                     .groupby(["gvkey", "fyearq", "fqtr"])
                     .last()
                     .reset_index()
                     .sort_values(["gvkey", "date", "rdq"])
                     .groupby(["gvkey", "date"])
                     .first()
                     .reset_index()
                     .query("rdq.isna() or date < rdq")
                     )

        processed_data = (
            compustat
            .get(["gvkey", "date", "datadate", "atq", "ceqq"]
                 + ([col for col in additional_columns.split(", ")]
                    if additional_columns else [])
                 )
            )

    return processed_data


def download_data_wrds_fisd(
    additional_columns: list = None
) -> pd.DataFrame:
    """
    Download a filtered subset of the FISD from WRDS.

    Parameters
    ----------
        additional_columns (list, optional): Additional columns from the FISD
        table to include.

    Returns
    -------
        pd.DataFrame: A DataFrame containing filtered FISD data with bond
        characteristics and issuer information.
    """
    wrds_connection = get_wrds_connection()

    fisd_query = (
        "SELECT complete_cusip, maturity, offering_amt, offering_date, "
        "dated_date, interest_frequency, coupon, last_interest_date, "
        "issue_id, issuer_id "
        "FROM fisd.fisd_mergedissue "
        "WHERE security_level = 'SEN' "
        "AND (slob = 'N' OR slob IS NULL) "
        "AND security_pledge IS NULL "
        "AND (asset_backed = 'N' OR asset_backed IS NULL) "
        "AND (defeased = 'N' OR defeased IS NULL) "
        "AND defeased_date IS NULL "
        "AND bond_type IN ('CDEB', 'CMTN', 'CMTZ', 'CZ', 'USBN') "
        "AND (pay_in_kind != 'Y' OR pay_in_kind IS NULL) "
        "AND pay_in_kind_exp_date IS NULL "
        "AND (yankee = 'N' OR yankee IS NULL) "
        "AND (canadian = 'N' OR canadian IS NULL) "
        "AND foreign_currency = 'N' "
        "AND coupon_type IN ('F', 'Z') "
        "AND fix_frequency IS NULL "
        "AND coupon_change_indicator = 'N' "
        "AND interest_frequency IN ('0', '1', '2', '4', '12') "
        "AND rule_144a = 'N' "
        "AND (private_placement = 'N' OR private_placement IS NULL) "
        "AND defaulted = 'N' "
        "AND filing_date IS NULL "
        "AND settlement IS NULL "
        "AND convertible = 'N' "
        "AND exchange IS NULL "
        "AND (putable = 'N' OR putable IS NULL) "
        "AND (unit_deal = 'N' OR unit_deal IS NULL) "
        "AND (exchangeable = 'N' OR exchangeable IS NULL) "
        "AND perpetual = 'N' "
        "AND (preferred_security = 'N' OR preferred_security IS NULL)"
        )

    fisd = pd.read_sql_query(
        sql=fisd_query,
        con=wrds_connection,
        dtype={"complete_cusip": str, "interest_frequency": str,
               "issue_id": int, "issuer_id": int},
        parse_dates={"maturity", "offering_date",
                     "dated_date", "last_interest_date"}
        )

    fisd_issuer_query = (
        "SELECT issuer_id, sic_code, country_domicile "
        "FROM fisd.fisd_mergedissuer"
        )

    fisd_issuer = pd.read_sql_query(
        sql=fisd_issuer_query,
        con=wrds_connection,
        dtype={"issuer_id": int, "sic_code": str, "country_domicile": str}
        )

    fisd = (fisd
            .merge(fisd_issuer, how="inner", on="issuer_id")
            .query("country_domicile == 'USA'")
            .drop(columns="country_domicile")
            )

    disconnect_connection(wrds_connection)

    return fisd


def download_data_wrds_trace_enhanced(
    cusips: list,
    start_date: str = None,
    end_date: str = None
) -> pd.DataFrame:
    """
    Download and clean Enhanced TRACE data from WRDS for specified CUSIPs.

    Parameters
    ----------
        cusips (list): A list of 9-digit CUSIPs to download.
        start_date (str, optional): Start date in "YYYY-MM-DD" format.
        Defaults to None.
        end_date (str, optional): End date in "YYYY-MM-DD" format.
        Defaults to None.

    Returns
    -------
        pd.DataFrame: A DataFrame containing cleaned TRACE trade messages for
        the specified CUSIPs.
    """
    if not all(isinstance(cusip, str) and len(cusip) == 9 for cusip in cusips):
        raise ValueError("All CUSIPs must be 9-character strings.")

    wrds_connection = get_wrds_connection()

    query = f"""
        SELECT cusip_id, trd_exctn_dt, trd_exctn_tm, rptd_pr, entrd_vol_qt,
               yld_pt, rpt_side_cd, cntra_mp_id, trc_st, asof_cd
        FROM trace.trace_enhanced
        WHERE cusip_id IN ({','.join(f"'{cusip}'" for cusip in cusips)})
    """

    if start_date and end_date:
        query += f" AND trd_exctn_dt BETWEEN '{start_date}' AND '{end_date}'"

    trace_data = pd.read_sql(query, wrds_connection)
    disconnect_wrds_connection(wrds_connection)

    trace_data = process_trace_data(trace_data)

    return trace_data
