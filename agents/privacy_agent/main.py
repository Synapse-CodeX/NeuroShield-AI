from agents.privacy_agent.graph import build_graph
from agents.privacy_agent.chat_agent import ask_privacy_question
import json


if __name__ == "__main__":
    print("🔐 Privacy Policy Analyzer (CLI Mode)\n")

    # 🔹 Sample input (you can paste your own)
    raw_text = """
Privacy Policy

This Privacy Policy describes how we collect, use, disclose, and protect your information when you use our application, website, and related services.

Information We Collect

We collect various types of personal information to provide and improve our services. This includes your name, email address, phone number, postal address, date of birth, and account credentials when you register. We may also collect location data, IP address, device identifiers, browser type, and operating system details.

In addition, we collect behavioral data such as pages visited, time spent on the platform, clicks, interactions, and usage patterns. If you use certain features, we may collect sensitive information such as preferences, interests, and demographic details.

How We Use Your Information

We use your personal data to operate, maintain, and improve our services. This includes personalizing content, recommending products, and enhancing user experience. Your data may also be used for marketing purposes, including sending promotional emails, advertisements, and offers tailored to your interests.

We may analyze user behavior using analytics tools to understand trends and improve our platform. Additionally, we may use your information for fraud detection, security monitoring, and compliance with legal obligations.

Sharing of Information

We may share your personal information with third-party partners, including advertisers, marketing agencies, analytics providers, and service vendors. These third parties may use your data for targeted advertising, campaign optimization, and business analytics.

We may also share information with affiliates and subsidiaries within our corporate group. In certain situations, your data may be disclosed to law enforcement or government authorities if required by law.

Tracking Technologies

We use cookies, web beacons, pixels, and similar tracking technologies to collect information about your browsing behavior. These technologies help us understand user engagement, track conversions, and deliver personalized advertisements.

We may also use third-party tracking tools that monitor your activity across different websites and platforms.

Data Retention

We retain your personal data for as long as necessary to fulfill the purposes outlined in this policy. In some cases, this may result in indefinite retention of certain information, particularly for analytics, legal, or operational purposes.

Even if you delete your account, we may retain some information to comply with legal obligations, resolve disputes, or enforce our agreements.

Data Security

We implement reasonable administrative, technical, and physical safeguards to protect your information. However, no method of transmission over the internet or electronic storage is completely secure, and we cannot guarantee absolute security.

Your Rights

Depending on your location, you may have rights regarding your personal data, including access, correction, deletion, and restriction of processing. You may also opt out of marketing communications at any time.

However, exercising these rights may limit your ability to use certain features of our services.

Children’s Privacy

Our services are not intended for individuals under the age of 13. We do not knowingly collect personal information from children. If we become aware that we have collected such data, we will take steps to delete it.

Changes to This Policy

We may update this Privacy Policy from time to time. Changes will be posted on this page, and continued use of our services constitutes acceptance of the updated policy.

Contact Us

If you have any questions or concerns about this Privacy Policy, please contact us at support@example.com.    

"""

    # 🔹 Build graph
    app = build_graph()

    # 🔹 Run pipeline
    print("⚙️ Running analysis...\n")
    result = app.invoke({"raw_text": raw_text})

    # 🔹 Clean output (avoid vector_store crash)
    safe_result = {
        "structured_data": result.get("structured_data"),
        "risks": result.get("risks"),
        "score": result.get("score"),
        "summary": result.get("summary"),
    }

    import json
    print("📊 RESULT:\n")
    print(json.dumps(safe_result, indent=2))

    # 🔹 Optional Chat Loop
    print("\n💬 Ask questions about this policy (type 'exit' to quit)\n")

    while True:
        user_q = input("You: ")

        if user_q.lower() in ["exit", "quit"]:
            break

        try:
            answer = ask_privacy_question(
                question=user_q,
                analysis_result=result,
                chat_history=[]
            )

            print(f"Agent: {answer}\n")

        except Exception as e:
            print(f"Error: {e}")
