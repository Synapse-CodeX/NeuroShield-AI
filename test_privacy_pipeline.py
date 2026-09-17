from agents.privacy_agent.graph import build_graph


SAMPLE_POLICY = """
We collect your name, email address, IP address, device information,
location information, and browsing activity.

We use your information to provide our services, improve our products,
personalize your experience, and deliver targeted advertising.

We may share your personal information with service providers,
analytics partners, advertising partners, and other business partners.

We use cookies, pixels, SDKs, and similar technologies to track usage
and measure advertising performance.

We retain personal information for as long as necessary to provide
our services and may retain certain information indefinitely when
required for legitimate business purposes.

You may contact us to request deletion of your personal information.
"""


def main():
    graph = build_graph()

    result = graph.invoke(
        {
            "raw_text": SAMPLE_POLICY,
        }
    )

    print("\n" + "=" * 70)
    print("NEUROSHIELD PRIVACY PIPELINE RESULT")
    print("=" * 70)

    print("\nSCORE:")
    print(result.get("score"))

    print("\nVERDICT:")
    print(result.get("verdict"))

    print("\nCONFIDENCE:")
    print(result.get("confidence"))

    print("\nRISKS:")
    for risk in result.get("risks", []):
        print(f"  - {risk}")

    print("\nSTRUCTURED DATA:")
    structured = result.get("structured_data", {})
    for key, value in structured.items():
        print(f"  {key}: {value}")

    print("\nFINDINGS:")
    for finding in result.get("findings", []):
        print(f"  [{finding.severity.upper()}] {finding.title}")
        print(f"    {finding.description}")
        print(f"    Confidence: {finding.confidence}")

    print("\nEVIDENCE:")
    for evidence in result.get("evidence", []):
        print(
            f"  - {evidence.title} "
            f"(relevance={evidence.relevance_score:.2f})"
        )
        print(f"    {evidence.excerpt[:250]}...")

    print("\nRECOMMENDATIONS:")
    for recommendation in result.get("recommendations", []):
        print(f"  - {recommendation}")

    print("\nSUMMARY:")
    print(result.get("summary"))

    print("\nREPORT:")
    report = result.get("report")
    if report:
        print(report.model_dump_json(indent=2))

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()