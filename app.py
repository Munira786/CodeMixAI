"""Streamlit interface for local CodeMixAI analysis and optional Gemini tools."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from ai_engine import (
    GeminiConfigurationError,
    analyze_code_mixed_text,
)
from chat_export import export_chat
from codemix_engine import LANGUAGES, analyze_text
from config import get_google_api_key
from error_handler import safe_error_message
from evaluation_engine import evaluate_dataset
from export_engine import (
    analyses_to_csv,
    analysis_to_csv,
    analysis_to_json,
    evaluation_to_csv,
)
from logger_engine import log_analysis, log_error
from memory_engine import add_message, clear_memory
from normalization_engine import normalize_text
from security_engine import validate_input
from smart_engine import smart_analyze


st.set_page_config(
    page_title="CodeMixAI",
    page_icon="🌐",
    layout="wide",
)

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []
if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None
if "last_smart_result" not in st.session_state:
    st.session_state.last_smart_result = None
if "evaluation_result" not in st.session_state:
    st.session_state.evaluation_result = None
if "ngrok_url" not in st.session_state:
    st.session_state.ngrok_url = None


def remember_analysis(result: dict) -> None:
    st.session_state.analysis_history.append(result)
    st.session_state.analysis_history = st.session_state.analysis_history[-100:]
    log_analysis(result["text"])


def render_analysis(result: dict, export_prefix: str = "codemix_analysis") -> None:
    columns = st.columns(4)
    columns[0].metric("Total words", result["total_words"])
    columns[1].metric("Unique words", result["unique_words"])
    columns[2].metric("Language switches", result["switching_count"])
    columns[3].metric("CMIS", f"{result['cmis']}/100")
    text_stats = st.columns(2)
    text_stats[0].metric("Characters", result["characters"])
    text_stats[1].metric("Average word length", result["average_word_length"])

    distribution = pd.DataFrame(
        {
            "Language": list(result["distribution"]),
            "Percentage": list(result["distribution"].values()),
        }
    )
    st.subheader("Language distribution")
    st.bar_chart(distribution.set_index("Language"))

    st.subheader("Code-Mixing Intelligence Score (CMIS)")
    st.progress(result["cmis"] / 100)
    st.write(f"**{result['cmis']}/100 — {result['cmis_level']}**")
    st.caption(
        "CMIS is the notebook's proposed heuristic score, not a validated "
        "research metric."
    )

    metrics = st.columns(4)
    metrics[0].metric("Mixing score", f"{result['mixing_score']}%")
    metrics[1].metric("Switching density", result["switching_density"])
    metrics[2].metric("Lexical diversity", result["lexical_diversity"])
    metrics[3].metric("Dominant language", result["dominant_language"])

    st.subheader("Local semantic heuristics")
    semantics = st.columns(2)
    semantics[0].metric("Sentiment", result["sentiment"])
    semantics[1].metric("Intent", result["intent"])
    st.caption(
        "Sentiment and intent are lightweight word-list heuristics; they are "
        "not machine-learned classifications."
    )

    st.subheader("Romanized words and dictionary gloss")
    transliterated = result["transliterated_words"]
    st.write(", ".join(transliterated) if transliterated else "None detected.")
    st.write(f"**Approximate normalization:** {normalize_text(result['text'])}")
    st.caption(
        "Normalization uses the notebook's small word dictionaries; it is not "
        "full transliteration or a general-purpose translation."
    )

    st.subheader("Language switching points")
    if result["switches"]:
        st.dataframe(pd.DataFrame(result["switches"]), use_container_width=True)
    else:
        st.info("No language switching detected.")

    st.subheader("Word-level language analysis")
    st.dataframe(
        pd.DataFrame(
            {
                "Word": result["words"],
                "Detected language": result["language_sequence"],
            }
        ),
        use_container_width=True,
    )

    st.subheader("Download this analysis")
    json_column, csv_column = st.columns(2)
    json_column.download_button(
        "Download JSON",
        data=analysis_to_json(result),
        file_name=f"{export_prefix}.json",
        mime="application/json",
        key=f"{export_prefix}_json",
    )
    csv_column.download_button(
        "Download CSV",
        data=analysis_to_csv(result),
        file_name=f"{export_prefix}.csv",
        mime="text/csv",
        key=f"{export_prefix}_csv",
    )


st.sidebar.title("🌐 CodeMixAI")
st.sidebar.caption("Code-mixed language understanding platform")
mode = st.sidebar.radio(
    "Navigation",
    ["Analyzer", "AI Assistant", "Smart Mode", "Analytics"],
)
st.sidebar.markdown("---")
st.sidebar.info(
    "Local word-list analysis for Romanized Gujarati, Romanized Hindi, "
    "and English."
)

with st.sidebar.expander("Optional public access (ngrok)"):
    st.caption("Local use does not require ngrok or an ngrok token.")
    if st.session_state.ngrok_url:
        st.success("Public tunnel is active.")
        st.code(st.session_state.ngrok_url, language=None)
        if st.button("Stop ngrok tunnel"):
            from ngrok_engine import stop_ngrok

            try:
                stop_ngrok()
                st.session_state.ngrok_url = None
                st.rerun()
            except RuntimeError as error:
                st.error(str(error))
    elif st.button("Start ngrok tunnel"):
        from ngrok_engine import start_ngrok

        try:
            st.session_state.ngrok_url = start_ngrok(port=8501)
            st.rerun()
        except (RuntimeError, ValueError) as error:
            st.error(str(error))

st.title("🌐 CodeMixAI")
st.caption("Local NLP + optional Gemini + code-mixed language intelligence")


if mode == "Analyzer":
    st.header("Code-mix analyzer")
    text = st.text_area(
        "Enter code-mixed text",
        height=160,
        placeholder="Aaje mara Python project ma error aave che.",
        key="analyzer_text",
    )
    if st.button("Analyze text", use_container_width=True):
        validation = validate_input(text)
        st.session_state.last_analysis = None
        if not validation["valid"]:
            st.error(validation["message"])
        else:
            result = analyze_text(text)
            st.session_state.last_analysis = result
            remember_analysis(result)

    if st.session_state.last_analysis:
        render_analysis(st.session_state.last_analysis)


elif mode == "AI Assistant":
    st.header("CodeMixAI conversational assistant")
    st.write(
        "Chat in English, Hindi, Gujarati, or a code-mixed style. "
        "Gemini is called only when you send a message."
    )
    if get_google_api_key():
        st.caption("Gemini configuration is present.")
    else:
        st.info(
            "Gemini is not configured. Add GOOGLE_API_KEY to your local "
            ".env file to enable AI replies; local analysis remains available."
        )

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_message = st.chat_input("Type your message...")
    if user_message:
        validation = validate_input(user_message)
        if not validation["valid"]:
            st.error(validation["message"])
        else:
            history = list(st.session_state.chat_messages)
            with st.chat_message("user"):
                st.markdown(user_message)
            from ai_engine import generate_response

            ai_result = generate_response(user_message, history)
            response = ai_result["response"]
            if not ai_result["success"]:
                st.warning(response)
                local_result = analyze_text(user_message)
                if "error" not in local_result:
                    languages = [
                        language
                        for language, percentage
                        in local_result["distribution"].items()
                        if percentage > 0
                    ]
                    response += (
                        "\n\n**Local Code-Mix Analysis**\n"
                        f"- Languages: {', '.join(languages)}\n"
                        f"- CMIS: {local_result['cmis']}/100\n"
                        f"- Mixing score: {local_result['mixing_score']}%\n"
                        f"- Language switches: "
                        f"{local_result['switching_count']}"
                    )
            with st.chat_message("assistant"):
                st.markdown(response)
            add_message(st.session_state.chat_messages, "user", user_message)
            add_message(st.session_state.chat_messages, "assistant", response)

    if st.session_state.chat_messages:
        if st.button("Clear conversation"):
            st.session_state.chat_messages = clear_memory()
            st.rerun()
        st.download_button(
            "Download this conversation as JSON",
            data=export_chat(st.session_state.chat_messages),
            file_name="codemixai_conversation.json",
            mime="application/json",
        )
        st.caption(
            "The export contains only this browser session's conversation and "
            "is generated only when you click download."
        )


elif mode == "Smart Mode":
    st.header("Smart code-mix analysis")
    st.write(
        "Local analysis always runs first. Choose whether to add a Gemini "
        "chat response, Gemini's structured analysis, or no AI request."
    )
    smart_text = st.text_area(
        "Enter code-mixed text",
        height=150,
        placeholder="Mujhe Python project banana hai but I don't know how.",
        key="smart_text",
    )
    ai_action = st.radio(
        "Optional AI action",
        ["Chat response", "Structured analysis", "Local only"],
        horizontal=True,
    )
    if st.button("Run smart analysis", use_container_width=True):
        validation = validate_input(smart_text)
        st.session_state.last_smart_result = None
        if not validation["valid"]:
            st.error(validation["message"])
        else:
            try:
                if ai_action == "Chat response":
                    result = smart_analyze(
                        smart_text,
                        st.session_state.chat_messages,
                    )
                    st.session_state.last_smart_result = {
                        "analysis": result["analysis"],
                        "response": result["ai_response"],
                        "ai_available": result["ai_available"],
                    }
                    remember_analysis(result["analysis"])
                else:
                    analysis = analyze_text(smart_text)
                    smart_result = {
                        "analysis": analysis,
                        "response": None,
                        "ai_available": None,
                    }
                    st.session_state.last_smart_result = smart_result
                    remember_analysis(analysis)
                    if ai_action == "Structured analysis":
                        smart_result["structured"] = (
                            analyze_code_mixed_text(smart_text).model_dump()
                        )
            except (GeminiConfigurationError, RuntimeError) as error:
                log_error(error)
                st.error(str(error))
            except Exception as error:
                log_error(error)
                st.error(safe_error_message(error))

    smart_result = st.session_state.last_smart_result
    if smart_result:
        render_analysis(smart_result["analysis"], "codemix_smart_analysis")
        if smart_result.get("response") is not None:
            if smart_result["ai_available"]:
                st.subheader("Gemini response")
                st.markdown(smart_result["response"])
            else:
                st.warning(smart_result["response"])
        if smart_result.get("structured") is not None:
            st.subheader("Gemini structured interpretation")
            st.json(smart_result["structured"])
            st.caption(
                "Gemini's interpretation is generated and may be approximate; "
                "the local metrics above remain independently computed."
            )


elif mode == "Analytics":
    st.header("Analysis history and evaluation")

    if st.session_state.analysis_history:
        history = st.session_state.analysis_history
        history_df = pd.DataFrame(
            [
                {
                    "Text": item["text"],
                    "Words": item["total_words"],
                    "CMIS": item["cmis"],
                    "Mixing score": item["mixing_score"],
                    "Switches": item["switching_count"],
                    "Dominant language": item["dominant_language"],
                }
                for item in history
            ]
        )
        st.subheader("This session's analysis history")
        st.dataframe(history_df, use_container_width=True)
        chart_left, chart_right = st.columns(2)
        with chart_left:
            st.bar_chart(history_df.set_index("Text")[["CMIS"]])
        with chart_right:
            mean_distribution = {
                language: sum(
                    item["distribution"][language] for item in history
                )
                / len(history)
                for language in LANGUAGES
            }
            st.bar_chart(
                pd.DataFrame(
                    {
                        "Language": list(mean_distribution),
                        "Mean percentage": list(mean_distribution.values()),
                    }
                ).set_index("Language")
            )
        st.download_button(
            "Download analysis history as CSV",
            data=analyses_to_csv(history),
            file_name="codemixai_analysis_history.csv",
            mime="text/csv",
        )
    else:
        st.info("Run an analysis to populate this session's history.")

    st.markdown("---")
    st.subheader("Notebook evaluation examples")
    st.caption(
        "Runs only on request. Metrics below compare the local detector with "
        "the notebook's eight sentence-level language tags. They are small "
        "dataset diagnostics, not token-level validation or research results."
    )
    if st.button("Run evaluation dataset"):
        try:
            st.session_state.evaluation_result = evaluate_dataset()
        except ImportError as error:
            st.error(
                "Evaluation dependencies are missing. Install requirements.txt "
                f"({type(error).__name__})."
            )

    evaluation = st.session_state.evaluation_result
    if evaluation:
        metrics = st.columns(4)
        metrics[0].metric(
            "Exact language-set match",
            f"{evaluation['exact_match_accuracy']:.1%}",
        )
        metrics[1].metric("Macro precision", f"{evaluation['precision']:.3f}")
        metrics[2].metric("Macro recall", f"{evaluation['recall']:.3f}")
        metrics[3].metric("Macro F1", f"{evaluation['f1']:.3f}")
        st.dataframe(pd.DataFrame(evaluation["records"]), use_container_width=True)

        distribution_totals = {
            language: sum(
                record[f"{language.lower()}_percentage"]
                for record in evaluation["records"]
            )
            / len(evaluation["records"])
            for language in LANGUAGES
        }
        chart_col, confusion_col = st.columns(2)
        with chart_col:
            st.subheader("Mean language distribution")
            st.bar_chart(
                pd.DataFrame(
                    {
                        "Language": list(distribution_totals),
                        "Mean percentage": list(distribution_totals.values()),
                    }
                ).set_index("Language")
            )
            st.subheader("CMIS per example")
            cmis_chart = pd.DataFrame(
                {
                    "Example": [
                        str(record["id"]) for record in evaluation["records"]
                    ],
                    "CMIS": [
                        record["cmis"] for record in evaluation["records"]
                    ],
                }
            )
            st.bar_chart(cmis_chart.set_index("Example"))

        with confusion_col:
            import matplotlib.pyplot as plt

            st.subheader("Per-language confusion matrices")
            figure, axes = plt.subplots(1, len(LANGUAGES), figsize=(10, 3))
            for axis, language in zip(axes, LANGUAGES):
                matrix = evaluation["confusion_matrices"][language]
                axis.imshow(matrix, cmap="Blues")
                axis.set_title(language)
                axis.set_xticks([0, 1], labels=["Absent", "Present"])
                axis.set_yticks([0, 1], labels=["Absent", "Present"])
                axis.set_xlabel("Predicted")
                axis.set_ylabel("Expected")
                for row in range(2):
                    for column in range(2):
                        axis.text(
                            column,
                            row,
                            str(matrix[row, column]),
                            ha="center",
                            va="center",
                        )
            figure.tight_layout()
            st.pyplot(figure)
            plt.close(figure)

        st.download_button(
            "Download evaluation results as CSV",
            data=evaluation_to_csv(evaluation["records"]),
            file_name="codemixai_evaluation.csv",
            mime="text/csv",
        )

st.sidebar.markdown("---")
st.sidebar.caption("CodeMixAI • Local NLP + optional Gemini")
st.sidebar.caption("Academic / research prototype")
