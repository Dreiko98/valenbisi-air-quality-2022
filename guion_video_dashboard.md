# Script for explanatory video — Dashboard Valenbisi × Air Quality 2022

---

## 1. Introduction and context (0:00 - 0:30)
**Screen:** Logo, dashboard title, and team names.

**Narration:**
> "Hello, we are Josep Ferrer García and Germán Mallo Faure. In this video, we present our project 'Valenbisi × Air Quality 2022', an interactive application that analyzes the relationship between public bicycle use and air quality in Valencia during 2022."

---

## 2. App benefits and motivation (0:30 - 1:00)
**Screen:** General view of the dashboard, sidebar, and KPIs.

**Narration:**
> "The goal of the application is to facilitate data-driven decision-making, both for citizens and the administration. It helps identify sustainable mobility patterns and their impact on pollution, supporting the promotion of healthier and more efficient transport policies."

---

## 3. Methodology and data pipeline (1:00 - 1:40)
**Screen:** Pipeline diagram (you can show the README or a slide with the data flow).

**Narration:**
> "To build the app, we started from open data from Valenbisi and air quality sources. We developed our own ETL pipeline: we downloaded, cleaned, and validated the data, aggregated it at city and station level, and linked it spatially. The result is datasets ready for exploratory analysis and visualization."

---

## 4. Data analysis and visualization (1:40 - 3:30)
**Screen:** Navigation through the dashboard sections, showing interactive charts and KPIs.

**Narration:**
> "The application has several interactive sections. In 'KPIs Summary' we show the main mobility and pollution indicators. In 'Temporal Analysis' we visualize the evolution of the data by months, days, and hours, identifying patterns and peaks. The 'Spatial Analysis' section allows you to explore the station map and compare city areas. In 'Correlations and Models' we analyze the relationship between variables and show a linear regression model to predict pollution based on bike use and meteorological factors. Finally, in 'Comparisons' we analyze differences between weekdays and weekends, and by months. All charts are interactive and allow filtering and detailed data exploration."

---

## 5. Technical details and development methodology (3:30 - 4:20)
**Screen:** Relevant code, folder structure, pipeline example, or code snippets.

**Narration:**
> "The app is developed in Python using Streamlit for the interface, Plotly for interactive visualizations, and scikit-learn for modeling. The ETL pipeline automates data download and cleaning. The code is modular and documented, making it easy to maintain and extend. All analysis and visualization logic is separated to ensure clarity and reproducibility."

---

## 6. Conclusions and closing (4:20 - 5:00)
**Screen:** General view of the dashboard and footer with names/link.

**Narration:**
> "In summary, our application allows intuitive and professional analysis of the relationship between sustainable mobility and air quality in Valencia. We hope it will be useful for decision-making and public awareness. Thank you very much for your attention. For more information, you can visit germanmallo.com."

---

> **Tip:** You can adapt the timing according to your explanation pace and show real interactivity (filters, station selection, etc.) during the demo. 