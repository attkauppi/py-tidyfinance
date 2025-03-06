"""Main module for tidyfinance package."""

import os
import yaml
import pandas as pd
import numpy as np
import requests
import webbrowser
import pandas_datareader as pdr
from sqlalchemy import create_engine, text

from _internal import (_trim,
                        _winsorize,
                        _validate_dates,
                        _return_datetime,
                        _transfrom_to_snake_case,
                        _assign_exchange,
                        _assign_industry
                        )


def add_lag_columns(
    data: pd.DataFrame,
    cols: list[str],
    by: str | None = None,
    lag: int = 0,
    max_lag: int | None = None,
    drop_na: bool = False,
    date_col: str = "date"
) -> pd.DataFrame:
    """
    Add lagged versions of specified columns to a Pandas DataFrame.

    Parameters
    ----------
        data (pd.DataFrame): The input DataFrame.
        cols (list[str]): List of column names to lag.
        by (str | None): Optional column to group by. Default is None.
        lag (int): Number of periods to lag. Must be non-negative.
        max_lag (int | None): Maximum lag period. Defaults to `lag` if None.
        drop_na (bool): Whether to drop rows with missing values in lagged
        columns. Default is False.
        date_col (str): The name of the date column. Default is "date".

    Returns
    -------
        pd.DataFrame: DataFrame with lagged columns appended.
    """
    if lag < 0 or (max_lag is not None and max_lag < lag):
        raise ValueError("`lag` must be non-negative, "
                         "and `max_lag` must be greater than or "
                         "equal to `lag`.")

    if max_lag is None:
        max_lag = lag

    # Ensure the date column is available
    if date_col not in data.columns:
        raise ValueError(f"Date column `{date_col}` not found in DataFrame.")

    result = data.copy()
    for col in cols:
        if col not in data.columns:
            raise ValueError(f"Column `{col}` not found in the DataFrame.")

        for index_lag in range(lag, max_lag + 1):
            lag_col_name = f"{col}_lag_{index_lag}"

            if by:
                result[lag_col_name] = result.groupby(by)[col].shift(index_lag)
            else:
                result[lag_col_name] = result[col].shift(index_lag)

            if drop_na:
                result = result.dropna(subset=[lag_col_name])

    return result


def assign_portfolio(data, sorting_variable, breakpoint_options=None, breakpoint_function=None, data_options=None):
    """Assign data points to portfolios based on a sorting variable.

    Parameters:
        data (pd.DataFrame): Data for portfolio assignment.
        sorting_variable (str): Column name used for sorting.
        breakpoint_options (dict, optional): Arguments for the breakpoint function.
        breakpoint_function (callable, optional): Function to compute breakpoints.
        data_options (dict, optional): Additional data processing options.

    Returns:
        pd.Series: Portfolio assignments for each row.
    """
    #     breakpoints = (data
    #                    .query("exchange == 'NYSE'")
    #                    .get(sorting_variable)
    #                    .quantile(percentiles, interpolation="linear")
    #                    )
    # breakpoints.iloc[0] = -np.Inf
    # breakpoints.iloc[breakpoints.size-1] = np.Inf
    
    # assigned_portfolios = pd.cut(
    #   data[sorting_variable],
    #   bins=breakpoints,
    #   labels=pd.Series(range(1, breakpoints.size)),
    #   include_lowest=True,
    #   right=False
    # )
    pass
    # return assigned_portfolios


def breakpoint_options(n_portfolios=None, percentiles=None, breakpoint_exchanges=None, smooth_bunching=False, **kwargs):
    """Create structured options for defining breakpoints.

    Parameters:
        n_portfolios (int, optional): Number of portfolios to create.
        percentiles (list, optional): Percentile thresholds for breakpoints.
        breakpoint_exchanges (list, optional): Exchanges for which breakpoints apply.
        smooth_bunching (bool): Whether to apply smooth bunching.
        kwargs: Additional optional parameters.

    Returns:
        dict: Breakpoint options.
    """
    pass

def compute_breakpoints(
    data: pd.DataFrame,
    sorting_variable: str,
    breakpoint_options: dict,
    data_options: dict = None
) -> np.ndarray:
    """Compute breakpoints based on a sorting variable.

    Parameters:
        data (pd.DataFrame): Data for breakpoint computation.
        sorting_variable (str): Column name for sorting.
        breakpoint_options (dict): Options for breakpoints.
        data_options (dict, optional): Additional data processing options.

    Returns:
        list: Computed breakpoints.
    """
    pass


def compute_long_short_returns(data, direction="top_minus_bottom", data_options=None):
    """Calculate long-short returns based on portfolio returns.

    Parameters:
        data (pd.DataFrame): Data containing portfolio returns.
        direction (str): Calculation direction ('top_minus_bottom' or 'bottom_minus_top').
        data_options (dict, optional): Additional data processing options.

    Returns:
        pd.DataFrame: DataFrame with computed long-short returns.
    """
    pass


def compute_portfolio_returns(sorting_data, sorting_variables, sorting_method, rebalancing_month=None, breakpoint_options_main=None, breakpoint_options_secondary=None, breakpoint_function_main=None, breakpoint_function_secondary=None, min_portfolio_size=0, data_options=None):
    """Compute portfolio returns based on sorting variables and methods.

    Parameters:
        sorting_data (pd.DataFrame): Data for portfolio assignment and return computation.
        sorting_variables (list): List of variables for sorting.
        sorting_method (str): Sorting method ('univariate' or 'bivariate').
        rebalancing_month (int, optional): Month for annual rebalancing.
        breakpoint_options_main (dict, optional): Options for main sorting variable.
        breakpoint_options_secondary (dict, optional): Options for secondary sorting variable.
        breakpoint_function_main (callable, optional): Function for main sorting.
        breakpoint_function_secondary (callable, optional): Function for secondary sorting.
        min_portfolio_size (int): Minimum portfolio size.
        data_options (dict, optional): Additional data processing options.

    Returns:
        pd.DataFrame: DataFrame with computed portfolio returns.
    """
    pass


def create_summary_statistics(data, *args, by=None, detail=False, drop_na=False):
    """Create summary statistics for specified variables.

    Parameters:
        data (pd.DataFrame): Data containing variables to summarize.
        *args: Variables to summarize.
        by (str, optional): Grouping variable.
        detail (bool): Whether to include detailed statistics.
        drop_na (bool): Whether to drop missing values.

    Returns:
        pd.DataFrame: Summary statistics.
    """
    pass


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


def data_options(id="permno", date="date", exchange="exchange", mktcap_lag="mktcap_lag", ret_excess="ret_excess", portfolio="portfolio", **kwargs):
    """Create a dictionary of data options for analysis.

    Parameters:
        id (str): Identifier variable name.
        date (str): Date variable name.
        exchange (str): Exchange variable name.
        mktcap_lag (str): Market capitalization lag variable.
        ret_excess (str): Excess return variable.
        portfolio (str): Portfolio variable.
        kwargs: Additional options.

    Returns:
        dict: Data options.
    """
    pass


def disconnection_connection(con):
    """Disconnect a database connection.

    Parameters:
        con (Any): Database connection object.

    Returns:
        bool: True if disconnection was successful, False otherwise.
    """
    pass


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
        url = f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?period1={start_timestamp}&period2={end_timestamp}&interval=1d"

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

    disconnect_wrds_connection(conn)

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
    else:
        raise ValueError("Invalid type specified. Use 'compustat_annual' or "
                         "'compustat_quarterly'.")

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

    disconnect_wrds_connection(wrds_connection)

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


def process_trace_data(
    trace_all: pd.DataFrame
) -> pd.DataFrame:
    """
    Process TRACE data by filtering trades, handling exception.

    Parameters
    ----------
        trace_all (pd.DataFrame): The raw TRACE data.

    Returns
    -------
        pd.DataFrame: The cleaned and processed TRACE data.
    """
    # Enhanced Trace: Post 06-02-2012 -----------------------------------------
    # Trades (trc_st = T) and correction (trc_st = R)
    trace_all['trd_rpt_dt'] = pd.to_datetime(trace_all['trd_rpt_dt'])
    trace_post_TR = (trace_all
                     .query("trc_st in ['T', 'R']")
                     .query("trd_rpt_dt >= '2012-02-06'")
                     )
    # Cancelations (trc_st = X) and correction cancelations (trc_st = C)
    trace_post_XC = (trace_all
                     .query("trc_st in ['X', 'C']")
                     .query("trd_rpt_dt >= '2012-02-06'")
                     )
    # Cleaning corrected and cancelled trades
    trace_post_TR = (trace_post_TR
                     .merge(trace_post_XC,
                            on=["cusip_id", "msg_seq_nb", "entrd_vol_qt",
                                "rptd_pr", "rpt_side_cd", "cntra_mp_id",
                                "trd_exctn_dt", "trd_exctn_tm"],
                            how='left',
                            indicator=True
                            )
                     .query("_merge == 'left_only'")
                     .drop(columns=['_merge'])
                     )

    # Reversals (trc_st = Y)
    trace_post_Y = (trace_all
                    .query("trc_st == 'S'")
                    .query("trd_rpt_dt >= '2012-02-06'")
                    )

    # Clean reversals
    # match the orig_msg_seq_nb of the Y-message to
    # the msg_seq_nb of the main message
    trace_post = (trace_post_TR
                  .merge(trace_post_Y
                         .rename(columns={"orig_msg_seq_nb": "msg_seq_nb"}),
                         on=["cusip_id", "msg_seq_nb", "entrd_vol_qt",
                             "rptd_pr", "rpt_side_cd", "cntra_mp_id",
                             "trd_exctn_dt", "trd_exctn_tm"],
                         how='left',
                         indicator=True
                         )
                  .query("_merge == 'left_only'")
                  .drop(columns=['_merge'])
                  )

    # Enhanced TRACE: Pre 06-02-2012 ------------------------------------------
    # Cancelations (trc_st = C)
    trace_pre_C = (trace_all
                   .query("trc_st == 'C'")
                   .query("trd_rpt_dt < '2012-02-06'")
                   )

    # Trades w/o cancelations
    # match the orig_msg_seq_nb of the C-message
    # to the msg_seq_nb of the main message
    trace_pre_T = (trace_all
                   .query("trc_st == 'T'")
                   .query("trd_rpt_dt < '2012-02-06'")
                   .merge(trace_pre_C
                          .rename(columns={"orig_msg_seq_nb": "msg_seq_nb"}),
                          on=["cusip_id", "msg_seq_nb", "entrd_vol_qt",
                              "rptd_pr", "rpt_side_cd", "cntra_mp_id",
                              "trd_exctn_dt", "trd_exctn_tm"],
                          how='left',
                          indicator=True
                          )
                   .query("_merge == 'left_only'")
                   .drop(columns=['_merge'])
                   )

    # Corrections (trc_st = W) - W can also correct a previous W
    trace_pre_W = (trace_all
                   .query("trc_st == 'W'")
                   .query("trd_rpt_dt < '2012-02-06'")
                   )
    # Implement corrections in a loop
    # Correction control
    correction_control = trace_pre_W.shape[0]
    correction_control_last = trace_pre_W.shape[0]

    # Correction loop
    while correction_control > 0:
        # Corrections that correct some messages
        trace_pre_W_correcting = (trace_pre_W.merge(
            trace_pre_T.rename(columns={"msg_seq_nb": "orig_msg_seq_nb"}),
            on=["cusip_id", "trd_exctn_dt", "orig_msg_seq_nb"],
            how="inner"
            )
            .get(trace_pre_W.columns)
            )

        # Corrections that do not correct some messages (anti-join)
        trace_pre_W = (trace_pre_W.merge(
            trace_pre_T.rename(columns={"msg_seq_nb": "orig_msg_seq_nb"}),
            on=["cusip_id", "trd_exctn_dt", "orig_msg_seq_nb"],
            how="left",
            indicator=True
            )
            .query('_merge == "left_only"')
            .drop(columns=["_merge"])
            )

        # Delete messages that are corrected and add correction messages
        trace_pre_T = (trace_pre_T.merge(
            trace_pre_W_correcting
            .rename(columns={"orig_msg_seq_nb": "msg_seq_nb"}),
            on=["cusip_id", "trd_exctn_dt", "msg_seq_nb"],
            how="left",
            indicator=True
            )
            .query('_merge == "left_only"')
            .drop(columns=["_merge"])
            )

        # Append correction messages
        trace_pre_T = pd.concat([trace_pre_T, trace_pre_W_correcting],
                                ignore_index=True
                                )

        # Escape if no corrections remain or they cannot be matched
        correction_control = trace_pre_W.shape[0]

        if correction_control == correction_control_last:
            correction_control = 0  # Break the loop if no changes

        correction_control_last = trace_pre_W.shape[0]

    # Clean reversals
    # Record reversals
    trace_pre_R = (
        trace_pre_T
        .query("asof_cd == 'R'")
        .groupby(['cusip_id', 'trd_exctn_dt', 'entrd_vol_qt',
                  'rptd_pr', 'rpt_side_cd', 'cntra_mp_id'])
        .apply(lambda x: x.sort_values(['trd_exctn_tm', 'trd_rpt_dt',
                                        'trd_rpt_tm'])
               .reset_index(drop=True)
               .assign(seq=range(1, len(x) + 1))
               )
        .reset_index(drop=True)
    )

    # Remove reversals and the reversed trade
    trace_pre = (
        trace_pre_T
        .query("asof_cd.isna() or asof_cd not in ['R', 'X', 'D']")
        .groupby(['cusip_id', 'trd_exctn_dt', 'entrd_vol_qt',
                  'rptd_pr', 'rpt_side_cd', 'cntra_mp_id'])
        .apply(lambda x: x.sort_values(['trd_exctn_tm', 'trd_rpt_dt',
                                        'trd_rpt_tm'])
               .reset_index(drop=True)
               .assign(seq=range(1, len(x) + 1))
               )
        .reset_index(drop=True)
        .merge(trace_pre_R,
               on=['cusip_id', 'trd_exctn_dt', 'entrd_vol_qt',
                   'rptd_pr', 'rpt_side_cd', 'cntra_mp_id', 'seq'],
               how='left',
               indicator=True)
        .query("_merge == 'left_only'")
        .drop(columns=['seq', '_merge'])
    )

    # Agency trades -----------------------------------------------------------
    # Combine pre and post trades
    trace_clean = pd.concat([trace_post, trace_pre], ignore_index=True)

    # Keep angency sells and unmatched agency buys
    # Agency sells
    trace_agency_sells = (trace_clean
                          .query("cntra_mp_id == 'D'")
                          .query("rpt_side_cd == 'S'")
                          )

    # Agency buys that are unmatched
    trace_agency_buys_filtered = (
        trace_clean
        .query("cntra_mp_id == 'D'")
        .query("rpt_side_cd == 'B'")
        .merge(trace_agency_sells,
               on=["cusip_id", "trd_exctn_dt", "entrd_vol_qt", "rptd_pr"],
               how="left",
               indicator=True)
        .query('_merge == "left_only"')
        .drop(columns=["_merge"])
    )

    # Agency clean
    trace_clean = (
        trace_clean
        .query("cntra_mp_id == 'C'")
        .pipe(pd.concat,
              [trace_agency_sells, trace_agency_buys_filtered],
              ignore_index=True
              )
    )

    # Additional Filters
    trace_clean["days_to_sttl_ct2"] = (trace_clean["stlmnt_dt"]
                                       .sub(trace_clean["trd_exctn_dt"])
                                       )

    trace_add_filters = (
        trace_clean
        .query("days_to_sttl_ct.isna() or days_to_sttl_ct.astype(float) <= 7")
        .query("days_to_sttl_ct2.isna() or days_to_sttl_ct2.astype(float)<=7")
        .query("wis_fl == 'N'")
        .query("spcl_trd_fl.isna() or spcl_trd_fl == ''")
        .query("asof_cd.isna() or asof_cd == ''")
        )

    # Output ------------------------------------------------------------------
    # Only keep necessary columns
    trace_final = (
        trace_add_filters
        .sort_values(["cusip_id", "trd_exctn_dt", "trd_exctn_tm"])
        .get(["cusip_id", "trd_exctn_dt", "trd_exctn_tm", "rptd_pr",
              "entrd_vol_qt", "yld_pt", "rpt_side_cd", "cntra_mp_id"]
             )
        .assign(trd_exctn_tm=lambda x:
                pd.to_datetime(x["trd_exctn_tm"]).dt.strftime("%H:%M:%S")
                )
        )

    return trace_final


def estimate_betas(data, model, lookback, min_obs=None, use_furrr=False, data_options=None):
    """Estimate rolling betas for a specified model.

    Parameters:
        data (pd.DataFrame): Data containing identifiers and model variables.
        model (str): Formula for the model (e.g., 'ret_excess ~ mkt_excess').
        lookback (int): Lookback period for rolling estimation.
        min_obs (int, optional): Minimum observations for estimation.
        use_furrr (bool): Whether to use parallel processing.
        data_options (dict, optional): Additional data options.

    Returns:
        pd.DataFrame: Estimated betas.
    """
    pass


def estimate_fama_macbeth(data, model, vcov="newey-west", vcov_options=None, data_options=None):
    """Estimate Fama-MacBeth regressions.

    Parameters:
        data (pd.DataFrame): Data for cross-sectional regressions.
        model (str): Formula for the regression model.
        vcov (str): Type of standard errors ('iid' or 'newey-west').
        vcov_options (dict, optional): Options for covariance matrix estimation.
        data_options (dict, optional): Additional data options.

    Returns:
        pd.DataFrame: Regression results with risk premiums and t-statistics.
    """
    pass


def estimate_model(data, model, min_obs=1):
    """Estimate coefficients of a linear model.

    Parameters:
        data (pd.DataFrame): Data for model estimation.
        model (str): Formula for the model (e.g., 'ret_excess ~ mkt_excess').
        min_obs (int): Minimum observations for estimation.

    Returns:
        pd.DataFrame: Model coefficients.
    """
    pass


def get_random_user_agent():
    """Retrieve a random user agent string.

    Returns
    -------
        str: A random user agent string.
    """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
        "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
        "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.110 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:117.0) Gecko/20100101 Firefox/117.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:116.0) Gecko/20100101 Firefox/116.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.141 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_6_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_7_8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.110 Safari/537.36 Edg/116.0.1938.69"
        ]
    return str(np.random.choice(user_agents))


def get_wrds_connection(config_path: str = "config.yaml") -> object:
    """
    Establish a connection to Wharton Research Data Services (WRDS) database.

    The function retrieves WRDS credentials from environment variables or
    a config.yaml file  and connects to the WRDS PostgreSQL database using
    SQLAlchemy.

    Parameters
    ----------
        config_path (str): Path to the configuration file.
        Default is "config.yaml".

    Returns
    -------
        object: A connection object to interact with the WRDS database.
    """
    wrds_user, wrds_password = load_wrds_credentials(config_path)

    engine = create_engine((f"postgresql://{wrds_user}:{wrds_password}"
                            "@wrds-pgdata.wharton.upenn.edu:9737/wrds"
                            ),
                           connect_args={"sslmode": "require"}
                           )
    return engine.connect()


def disconnect_wrds_connection(
    connection: object
) -> bool:
    """Close the WRDS database connection.

    Parameters
    ----------
        connection (object): The active database connection to be closed.

    Returns
    -------
        bool: True if disconnection was successful, False otherwise.
    """
    try:
        connection.close()
        return True
    except Exception:
        return False


def list_supported_indexes(
) -> pd.DataFrame:
    """
    Return a DataFrame containing information on supported financial indexes.

    Each index is associated with a URL pointing to a CSV file containing
    the holdings of the index and a `skip` value indicating the number of
    lines to skip when reading the CSV.

    Returns
    -------
        pd.DataFrame: A DataFrame with three columns:
            - index (str): The name of the financial index
            (e.g., "DAX", "S&P 500").
            - url (str): The URL to the CSV file containing holdings data.
            - skip (int): The number of lines to skip when reading CSV file.
    """
    data = [
        ("DAX", "https://www.ishares.com/de/privatanleger/de/produkte/251464/ishares-dax-ucits-etf-de-fund/1478358465952.ajax?fileType=csv&fileName=DAXEX_holdings&dataType=fund", 2),
        ("EURO STOXX 50", "https://www.ishares.com/de/privatanleger/de/produkte/251783/ishares-euro-stoxx-50-ucits-etf-de-fund/1478358465952.ajax?fileType=csv&fileName=EXW1_holdings&dataType=fund", 2),
        ("Dow Jones Industrial Average", "https://www.ishares.com/de/privatanleger/de/produkte/251770/ishares-dow-jones-industrial-average-ucits-etf-de-fund/1478358465952.ajax?fileType=csv&fileName=EXI3_holdings&dataType=fund", 2),
        ("Russell 1000", "https://www.ishares.com/ch/professionelle-anleger/de/produkte/239707/ishares-russell-1000-etf/1495092304805.ajax?fileType=csv&fileName=IWB_holdings&dataType=fund", 9),
        ("Russell 2000", "https://www.ishares.com/ch/professionelle-anleger/de/produkte/239710/ishares-russell-2000-etf/1495092304805.ajax?fileType=csv&fileName=IWM_holdings&dataType=fund", 9),
        ("Russell 3000", "https://www.ishares.com/ch/professionelle-anleger/de/produkte/239714/ishares-russell-3000-etf/1495092304805.ajax?fileType=csv&fileName=IWV_holdings&dataType=fund", 9),
        ("S&P 100", "https://www.ishares.com/ch/professionelle-anleger/de/produkte/239723/ishares-sp-100-etf/1495092304805.ajax?fileType=csv&fileName=OEF_holdings&dataType=fund", 9),
        ("S&P 500", "https://www.ishares.com/de/privatanleger/de/produkte/253743/ishares-sp-500-b-ucits-etf-acc-fund/1478358465952.ajax?fileType=csv&fileName=SXR8_holdings&dataType=fund", 2),
        ("Nasdaq 100", "https://www.ishares.com/de/privatanleger/de/produkte/251896/ishares-nasdaq100-ucits-etf-de-fund/1478358465952.ajax?fileType=csv&fileName=EXXT_holdings&dataType=fund", 2),
        ("FTSE 100", "https://www.ishares.com/de/privatanleger/de/produkte/251795/ishares-ftse-100-ucits-etf-inc-fund/1478358465952.ajax?fileType=csv&fileName=IUSZ_holdings&dataType=fund", 2),
        ("MSCI World", "https://www.ishares.com/de/privatanleger/de/produkte/251882/ishares-msci-world-ucits-etf-acc-fund/1478358465952.ajax?fileType=csv&fileName=EUNL_holdings&dataType=fund", 2),
        ("Nikkei 225", "https://www.ishares.com/ch/professionelle-anleger/de/produkte/253742/ishares-nikkei-225-ucits-etf/1495092304805.ajax?fileType=csv&fileName=CSNKY_holdings&dataType=fund", 2),
        ("TOPIX", "https://www.blackrock.com/jp/individual-en/en/products/279438/fund/1480664184455.ajax?fileType=csv&fileName=1475_holdings&dataType=fund", 2)
    ]
    return pd.DataFrame(data, columns=["index", "url", "skip"])


def list_supported_types(domain=None, as_vector=False):
    """List all supported dataset types.

    Parameters:
        domain (list, optional): Filter for specific domains.
        as_vector (bool): Whether to return as a list instead of DataFrame.

    Returns:
        Union[pd.DataFrame, list]: Supported dataset types.
    """
    pass


def list_tidy_finance_chapters(
) -> list:
    """
    Return a list of available chapters in the Tidy Finance resource.

    Returns
    -------
        list: A list where each element is the name of a chapter available in
        the Tidy Finance resource.
    """
    return [
        "setting-up-your-environment",
        "introduction-to-tidy-finance",
        "accessing-and-managing-financial-data",
        "wrds-crsp-and-compustat",
        "trace-and-fisd",
        "other-data-providers",
        "beta-estimation",
        "univariate-portfolio-sorts",
        "size-sorts-and-p-hacking",
        "value-and-bivariate-sorts",
        "replicating-fama-and-french-factors",
        "fama-macbeth-regressions",
        "fixed-effects-and-clustered-standard-errors",
        "difference-in-differences",
        "factor-selection-via-machine-learning",
        "option-pricing-via-machine-learning",
        "parametric-portfolio-policies",
        "constrained-optimization-and-backtesting",
        "wrds-dummy-data",
        "cover-and-logo-design",
        "clean-enhanced-trace-with-r",
        "proofs",
        "changelog"
    ]


def load_wrds_credentials(
    config_path: str = "config.yaml"
) -> tuple:
    """
    Load WRDS credentials from a config.yaml file if env variables are not set.

    Parameters
    ----------
        config_path (str): Path to the configuration file.
        Default is "config.yaml".

    Returns
    -------
        tuple: A tuple containing (wrds_user (str), wrds_password (str)).
    """
    wrds_user: str = os.getenv("WRDS_USER")
    wrds_password: str = os.getenv("WRDS_PASSWORD")

    if not wrds_user or not wrds_password:
        if os.path.exists(config_path):
            with open(config_path, "r") as file:
                config = yaml.safe_load(file)
                wrds_user = config.get("WRDS", {}).get("USER", "")
                wrds_password = config.get("WRDS", {}).get("PASSWORD", "")

    if not wrds_user or not wrds_password:
        raise ValueError("WRDS credentials not found. Please set 'WRDS_USER' "
                         "and 'WRDS_PASSWORD' as environment variables or "
                         "in config.yaml.")

    return wrds_user, wrds_password


def open_tidy_finance_website(
    chapter: str = None
) -> None:
    """Open the Tidy Finance website or a specific chapter in a browser.

    Parameters
    ----------
        chapter (str, optional): Name of the chapter to open. Defaults to None.

    Returns
    -------
        None
    """
    base_url = "https://www.tidy-finance.org/python/"

    if chapter:
        tidy_finance_chapters = list_tidy_finance_chapters()
        if chapter in tidy_finance_chapters:
            final_url = f"{base_url}{chapter}.html"
        else:
            final_url = base_url
    else:
        final_url = base_url

    webbrowser.open(final_url)


def set_wrds_credentials() -> None:
    """Set WRDS credentials in the environment.

    Prompts the user for WRDS credentials and stores them in a YAML
    configuration file.

    The user can choose to store the credentials in the project directory or
    the home directory. If credentials already exist, the user is prompted for
    confirmation before overwriting them. Additionally, the user is given an
    option to add the configuration file to .gitignore.

    Returns
    -------
        - Saves the WRDS credentials in a `config.yaml` file
        - Optionally adds `config.yaml` to `.gitignore`
    """
    wrds_user = input("Enter your WRDS username: ")
    wrds_password = input("Enter your WRDS password: ")
    location_choice = (input("Where do you want to store the config.yaml "
                             "file? Enter 'project' for project directory or "
                             "'home' for home directory: ")
                       .strip().lower()
                       )

    if location_choice == "project":
        config_path = os.path.join(os.getcwd(), "config.yaml")
        gitignore_path = os.path.join(os.getcwd(), ".gitignore")
    elif location_choice == "home":
        config_path = os.path.join(os.path.expanduser("~"), "config.yaml")
        gitignore_path = os.path.join(os.path.expanduser("~"), ".gitignore")
    else:
        print("Invalid choice. Please start again and enter "
              "'project' or 'home'.")
        return

    config: dict = {}
    if os.path.exists(config_path):
        with open(config_path, "r") as file:
            config = yaml.safe_load(file) or {}

    if "WRDS" in config and "USER" in config["WRDS"] and "PASSWORD" in config["WRDS"]:
        overwrite_choice = (input("Credentials already exist. Do you want to "
                                  "overwrite them? Enter 'yes' or 'no': ")
                            .strip().lower()
                            )
        if overwrite_choice != "yes":
            print("Aborted. Credentials already exist and are not "
                  "overwritten.")
            return

    if os.path.exists(gitignore_path):
        add_gitignore = (input("Do you want to add config.yaml to .gitignore? "
                               "It is highly recommended! "
                               "Enter 'yes' or 'no': ")
                         .strip().lower()
                         )
        if add_gitignore == "yes":
            with open(gitignore_path, "r") as file:
                gitignore_lines = file.readlines()
            if "config.yaml\n" not in gitignore_lines:
                with open(gitignore_path, "a") as file:
                    file.write("config.yaml\n")
                print("config.yaml added to .gitignore.")
        elif add_gitignore == "no":
            print("config.yaml NOT added to .gitignore.")
        else:
            print("Invalid choice. Please start again "
                  "and enter 'yes' or 'no'.")
            return

    config["WRDS"] = {"USER": wrds_user, "PASSWORD": wrds_password}

    with open(config_path, "w") as file:
        yaml.safe_dump(config, file)

    print("WRDS credentials have been set and saved in config.yaml in your "
          f"{location_choice} directory.")









