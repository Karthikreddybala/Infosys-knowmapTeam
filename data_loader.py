import pandas as pd

def load_ai_dataset(filepath="arxiv_ai.csv", max_rows=500):
    """
    ArXiv AI dataset — uses title + summary as text.
    """
    df = pd.read_csv(filepath)
    df = df[['title', 'summary']].dropna()
    df = df.head(max_rows)
    df['text'] = df['title'] + ". " + df['summary']
    df['domain'] = 'AI'
    print(f"✅ AI Dataset loaded: {len(df)} rows")
    return df[['text', 'domain']]


def load_cybersecurity_dataset(filepath="ai_ml_cybersecurity_dataset.csv", max_rows=500):
    """
    Cybersecurity dataset — uses Attack Type + Threat Intelligence + Response Action as text.
    These columns contain the most meaningful text for NLP.
    """
    df = pd.read_csv(filepath)
    df = df[['Attack Type', 'Threat Intelligence', 'Response Action']].dropna()
    df = df.head(max_rows)

    # Combine into one descriptive sentence per row
    df['text'] = (
        "Attack type is " + df['Attack Type'] + ". " +
        df['Threat Intelligence'] + ". " +
        "Response action: " + df['Response Action'] + "."
    )
    df['domain'] = 'Cybersecurity'
    print(f"✅ Cybersecurity Dataset loaded: {len(df)} rows")
    return df[['text', 'domain']]


def load_combined_dataset(ai_path="arxiv_ai.csv",
                          cyber_path="ai_ml_cybersecurity_dataset.csv",
                          max_rows=500):
    """
    Loads both datasets and combines into one DataFrame.
    """
    ai_df    = load_ai_dataset(ai_path, max_rows)
    cyber_df = load_cybersecurity_dataset(cyber_path, max_rows)

    combined = pd.concat([ai_df, cyber_df], ignore_index=True).dropna()

    print(f"\n✅ Combined Dataset: {len(combined)} total rows")
    print(f"   AI rows            : {len(combined[combined['domain']=='AI'])}")
    print(f"   Cybersecurity rows : {len(combined[combined['domain']=='Cybersecurity'])}")
    return combined


# ── TEST ──────────────────────────────────────────────
if __name__ == "__main__":
    df = load_combined_dataset()
    print("\n--- Sample AI text ---")
    print(df[df['domain'] == 'AI']['text'].iloc[0][:300])
    print("\n--- Sample Cybersecurity text ---")
    print(df[df['domain'] == 'Cybersecurity']['text'].iloc[0][:300])
