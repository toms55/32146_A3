import charts
import page
import read_workbook as rw
from layout import DIRECTIONS, ROOT, YEARS

OUT = ROOT / "docs" / "dashboard.html"

INTRO = (
    "One subcategory, examined in both trade directions. Subcategory 33 is the only large "
    "part of Australian trade where the country buys far more than it sells. Every chart "
    "below reads the Excel workbook, and every axis carries its unit."
)


def money(value):
    return f"{value:,.0f}"


def kpis(rows, summary):
    last = rows[-1]
    first = rows[0]
    export_cagr = (last["export"] / first["export"]) ** (1 / 9) - 1
    import_cagr = (last["import"] / first["import"]) ** (1 / 9) - 1
    return page.kpi_row(
        [
            page.kpi("Export 2025", f"${money(last['export'])}m", "Up from $6,946m in 2016", "export"),
            page.kpi("Import 2025", f"${money(last['import'])}m", "Up from $23,315m in 2016", "import"),
            page.kpi("Trade balance 2025", f"-${money(abs(last['balance']))}m", "Negative in all ten years", "negative"),
            page.kpi("Cover ratio 2025", f"{last['cover']:.2f}", "Export buys 27 cents of each import dollar", "focus"),
            page.kpi("Export growth a year", f"{export_cagr:.1%}", "Compound, 2016 to 2025", "export"),
            page.kpi("Import growth a year", f"{import_cagr:.1%}", "Compound, 2016 to 2025", "import"),
        ]
    )


def focus_table(rows):
    body = [
        [
            r["year"],
            money(r["export"]),
            money(r["import"]),
            money(r["balance"]),
            f"{r['cover']:.2f}",
            "" if r["export_growth"] is None else f"{r['export_growth']:.1%}",
            "" if r["import_growth"] is None else f"{r['import_growth']:.1%}",
        ]
        for r in rows
    ]
    return page.table(
        "Subcategory 33 petroleum, every year. Values in $ Millions.",
        ["Year", "Export", "Import", "Balance", "Cover ratio", "Export growth", "Import growth"],
        body,
    )


def growth_table(rows):
    body = [
        [
            r["year"],
            f"{r['export_growth']:.1%}",
            f"{r['import_growth']:.1%}",
        ]
        for r in rows[1:]
    ]
    return page.table(
        "Year on year growth of subcategory 33, both directions.",
        ["Year", "Export growth", "Import growth"],
        body,
        summary="Show the growth numbers behind this chart",
    )


def balance_table(rows):
    body = [
        [r["year"], money(r["balance"]), f"{r['cover']:.2f}"]
        for r in rows
    ]
    return page.table(
        "The petroleum trade balance and the cover ratio. Values in $ Millions.",
        ["Year", "Balance", "Cover ratio"],
        body,
        summary="Show the balance numbers behind this chart",
    )


def scatter_table(rows):
    body = [
        [r["year"], money(r["export"]), money(r["import"]), f"{r['import'] / r['export']:.2f}"]
        for r in rows
    ]
    return page.table(
        "The two values plotted against each other, one row for each point. Values in $ Millions.",
        ["Year", "Export", "Import", "Import divided by export"],
        body,
        summary="Show the points behind this chart",
    )


def moving_average_table(rows):
    body = [
        [
            r["year"],
            "" if r["export_ma"] is None else money(r["export_ma"]),
            "" if r["import_ma"] is None else money(r["import_ma"]),
        ]
        for r in rows
    ]
    return page.table(
        "The three year moving average of each direction, read from the Excel formula. "
        "Values in $ Millions.",
        ["Year", "Export, three year average", "Import, three year average"],
        body,
        summary="Show the moving average numbers behind this chart",
    )


def zscore_table(rows):
    body = [
        [r["year"], f"{r['export_z']:.2f}", f"{r['import_z']:.2f}"]
        for r in rows[1:]
    ]
    return page.table(
        "Growth z-scores. A value beyond plus or minus 2 marks an outlier year.",
        ["Year", "Export growth z-score", "Import growth z-score"],
        body,
        summary="Show the z-scores behind this chart",
    )


def pair_table(pairs):
    labels = {
        "33 against 32": "Petroleum against coal",
        "33 against 34": "Petroleum against gas",
        "32 against 34": "Coal against gas",
    }
    body = [
        [labels[key], f"{pairs[key]['Export']:.2f}", f"{pairs[key]['Import']:.2f}"]
        for key in labels
    ]
    return page.table(
        "Correlation of year on year growth for every pair inside mineral fuels.",
        ["Pair", "Export r", "Import r"],
        body,
        summary="Show the correlations behind this chart",
    )


def subcategory_table():
    names, export_index = rw.vs_index("Export")
    _, import_index = rw.vs_index("Import")
    body = []
    for code in export_index:
        body.append(
            [
                f"{code} {names[code]}",
                f"{export_index[code][-1]:,.0f}",
                f"{import_index[code][-1]:,.0f}",
            ]
        )
    return page.table(
        "Index of each subcategory in 2025, with 2016 set to 100.",
        ["Subcategory", "Export index 2025", "Import index 2025"],
        body,
        summary="Show the index numbers behind this chart",
    )


def forecast_table():
    rows = rw.forecast()[len(YEARS):]
    ai = rw.ai_comparison()
    body = [
        [
            row["year"],
            money(row["linear"]),
            money(row["cagr"]),
            money(row["target"]),
            money(entry["ai"]),
        ]
        for row, entry in zip(rows, ai)
    ]
    return page.table(
        "Petroleum import, the five forecast years. Values in $ Millions.",
        ["Year", "Linear trend", "CAGR method", "Target path", "Claude Sonnet 5"],
        body,
        summary="Show the forecast numbers behind this chart",
    )


def share_table():
    body = []
    for direction in DIRECTIONS:
        _, share = rw.cat3_share(direction)
        body.append(
            [
                f"Petroleum share of mineral fuels, {direction.lower()}",
                f"{share['33'][0]:.1%}",
                f"{share['33'][-1]:.1%}",
            ]
        )
    return page.table(
        "Petroleum as a share of mineral fuels.",
        ["Measure", "2016", "2025"],
        body,
        summary="Show the share numbers behind this chart",
    )


def insights(rows):
    items = "".join(
        f'<li><span class="yr">{r["year"]}</span><span class="txt">{r["insight"]}</span></li>'
        for r in rows
    )
    return f'<ul class="insights">{items}</ul>'


def main():
    rows = rw.focus()
    summary = rw.forecast_summary()
    ai = rw.ai_comparison()
    pairs, import_export_r = rw.vs_pairs()
    ratio_2025 = rows[-1]["import"] / rows[-1]["export"]
    _, share_export = rw.cat3_share("Export")
    _, share_import = rw.cat3_share("Import")

    out = page.head(
        "Petroleum dashboard, Australian trade 2016 to 2025",
        "A dashboard for SITC subcategory 33, petroleum, covering Australian import and export from 2016 to 2025.",
    )
    out += page.nav("dashboard.html")
    out += page.header(
        "Assessment task 3, dashboard",
        "Subcategory 33: petroleum, petroleum products and related materials",
        INTRO,
    )
    out += kpis(rows, summary)

    time_charts = ["cmp1", "cmp2", "cmp3", "cmp5", "cmp6", "cmp7", "cmp8"]
    out += page.year_control(time_charts, YEARS[0], YEARS[-1])

    out += page.panel(
        "Comparison 1. Export against import",
        "Both directions in dollars on one scale. The gap between the two lines is the trade "
        "deficit.",
        page.figure(charts.focus_export_import(), "cmp1") + focus_table(rows),
        takeaway=(
            "<strong>Import outruns export in every year.</strong> Import grew 126% across the "
            "decade and export grew 104%."
        ),
    )

    out += page.panel(
        "Comparison 2. Growth rate, export against import",
        "Year on year growth in per cent, so the small export series and the large import "
        "series compare fairly.",
        page.figure(charts.focus_growth(), "cmp2") + growth_table(rows),
        takeaway=(
            "<strong>The two directions turn in the same years.</strong> Both fall in 2020 and "
            "both jump in 2022, which is the first sign that one world price drives the pair."
        ),
    )

    out += page.panel(
        "Comparison 3. The trade balance",
        "Export minus import, for each year. Every column points down, so Australia bought "
        "more petroleum than it sold in all ten years.",
        page.figure(charts.focus_balance(), "cmp3") + balance_table(rows),
        takeaway=(
            "<strong>The deficit more than doubled.</strong> It widened from $16,369m in 2016 to "
            "$38,555m in 2025, and reached its worst point of $47,741m in 2022."
        ),
    )

    out += page.panel(
        "Comparison 4. Import against export, year by year",
        "Each point is one year, with a fitted line. If the two sides were independent the "
        "points would scatter. They do not.",
        page.figure(charts.focus_scatter(), "cmp4") + scatter_table(rows),
        takeaway=(
            f"<strong>The two directions move together at r = {import_export_r:.2f}.</strong> "
            f"Both sides are priced off the same world oil market, so a price rise lifts import "
            f"and export at once. Because import is {ratio_2025:.2f} times larger, every price "
            "rise widens the deficit."
        ),
    )

    out += page.panel(
        "Comparison 5. The three year moving average",
        "The smoothed trend of both directions. The thick line graphs the live Excel moving "
        "average formula and the dotted line is the value of each year.",
        page.figure(charts.focus_moving_average(), "cmp5") + moving_average_table(rows),
        takeaway=(
            "<strong>Smoothing removes the price spike and leaves the climb.</strong> The import "
            "average keeps rising through the decade, so the 2022 peak sits on a rising base "
            "rather than on a flat one."
        ),
    )

    out += page.panel(
        "Comparison 6. Growth outliers, z-score",
        "Growth distance from the mean in standard deviations, with the plus 2 and minus 2 "
        "thresholds marked.",
        page.figure(charts.focus_zscore(), "cmp6") + zscore_table(rows),
        takeaway=(
            "<strong>One year crosses the threshold.</strong> Import growth in 2022 reaches "
            f"z = {rows[6]['import_z']:.2f}, which makes it the only petroleum outlier of the "
            "decade. No export year passes plus or minus 2, so the price shock hit the import "
            "bill harder than it hit export earnings."
        ),
    )

    out += page.panel(
        "Comparison 7. Petroleum against its main category",
        "Petroleum as a share of mineral fuels, for import and for export. This shows how "
        "much of the energy category the subcategory carries on each side.",
        page.figure(charts.focus_share_of_main(), "cmp7") + share_table(),
        takeaway=(
            f"<strong>The two sides are not alike.</strong> Petroleum is "
            f"{share_export['33'][-1]:.1%} of mineral fuels export in 2025 and "
            f"{share_import['33'][-1]:.1%} of mineral fuels import, against "
            f"{share_import['32'][-1]:.1%} for coal and {share_import['34'][-1]:.1%} for gas."
        ),
    )

    out += page.panel(
        "Comparison 8. Petroleum against coal and gas",
        "The three subcategories of mineral fuels, indexed so that 2016 equals 100, each line "
        "labelled with its 2025 value. An index lets subcategories of very different size "
        "share one axis.",
        page.figure(charts.focus_vs_subcategories(), "cmp8") + subcategory_table(),
        takeaway=(
            "<strong>Gas grew fastest on the export side, and coal fell hardest after 2022.</strong> "
            f"Petroleum growth tracks coal at r = {pairs['33 against 32']['Export']:.2f} and gas at "
            f"r = {pairs['33 against 34']['Export']:.2f} on the export side."
        ),
    )

    out += page.panel(
        "Comparison 9. Growth correlation with coal and gas",
        "All six pair correlations, which is three pairs by two directions.",
        page.figure(charts.focus_pair_correlations(), "cmp9") + pair_table(pairs),
        takeaway=(
            "<strong>The export side holds together and the import side does not.</strong> "
            f"Petroleum tracks gas at r = {pairs['33 against 34']['Export']:.2f} on export but only "
            f"r = {pairs['33 against 34']['Import']:.2f} on import, because the coal and gas import "
            "series are small and noisy."
        ),
    )

    out += page.panel(
        "What happened in each year",
        "One line for every year from 2016 to 2025, read from the workbook.",
        insights(rows),
    )

    out += page.panel(
        "The 2030 outlook, and the Claude Sonnet 5 forecast",
        "Ten years of actual petroleum import, then five forecast years. The chart carries the "
        "linear trend, the CAGR method, a target path of 3% a year lower, and a forecast from "
        "Claude Sonnet 5. The model ran on 16 October 2026 with no tools. It received the ten "
        "annual import values and nothing else.",
        page.figure(charts.forecast_chart(), "outlook") + forecast_table(),
        takeaway=(
            "<strong>Claude Sonnet 5 forecasts a fall and the linear trend forecasts a rise.</strong> "
            f"The two differ by ${money(abs(ai[-1]['difference']))}m in 2030, which is more than "
            "the whole 2016 import bill. Page 3 backtests both methods against held out years and "
            "both miss widely, so the target path is the number to steer by."
        ),
    )

    out += page.footer()
    out += page.TAIL
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(out)
    size = OUT.stat().st_size / 1024 / 1024
    print(f"wrote {OUT.relative_to(ROOT)} ({size:.1f} MB)")


if __name__ == "__main__":
    main()
