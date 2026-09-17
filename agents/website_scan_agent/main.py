from agents.website_scan_agent.graph import build_graph
from agents.website_scan_agent.chat_agent import ask_website_safety_question
import json


if __name__ == "__main__":
    print("🔍 Website Safety Scanner (CLI Mode)\n")

    # 🔹 Get URL from user
    url = input("Enter URL to scan: ").strip()
    if not url:
        url = "https://example.com"
        print(f"Using default: {url}")

    # 🔹 Build graph
    app = build_graph()

    # 🔹 Run pipeline
    print("\n⚙️ Scanning website...\n")
    result = app.invoke({"url": url})

    # 🔹 Display results
    safe_result = {
        "url": result.get("url"),
        "scores": result.get("scores"),
        "overall_score": result.get("overall_score"),
        "verdict": result.get("verdict"),
        "recommendations": result.get("recommendations"),
    }

    print("=" * 60)
    print("📊 SCAN RESULTS")
    print("=" * 60)
    print(json.dumps(safe_result, indent=2))
    print("=" * 60)

    # 🔹 Detailed breakdown
    print("\n📋 DETAILED BREAKDOWN:\n")

    detail_keys = [
        ("url_analysis", "🔗 URL Structure"),
        ("domain_age_analysis", "📅 Domain Age"),
        ("scam_report_analysis", "🚨 Scam Reports"),
        ("ssl_analysis", "🔒 SSL Certificate"),
        ("content_analysis", "📝 Content Quality"),
        ("reputation_analysis", "⭐ Reputation"),
    ]

    for key, label in detail_keys:
        data = result.get(key, {})
        score = data.get("score", "N/A")
        print(f"  {label}: {score}/100")
        flags = data.get("flags", [])
        if flags:
            for f in flags:
                print(f"    ⚠️  {f}")

    # 🔹 Summary
    print(f"\n🏆 OVERALL SCORE: {result.get('overall_score', 'N/A')}/100")
    print(f"📌 VERDICT: {result.get('verdict', 'N/A')}")

    recs = result.get("recommendations", [])
    if recs:
        print("\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(recs, 1):
            print(f"  {i}. {rec}")

    # 🔹 Optional Chat Loop
    print("\n💬 Ask questions about this scan (type 'exit' to quit)\n")

    while True:
        user_q = input("You: ")

        if user_q.lower() in ["exit", "quit"]:
            break

        try:
            answer = ask_website_safety_question(
                question=user_q,
                analysis_result=result,
                chat_history=[],
            )
            print(f"Agent: {answer}\n")

        except Exception as e:
            print(f"Error: {e}")
