import random

# Large vocabularies
ai_methods = ["deep learning", "machine learning", "neural network", "reinforcement learning", "supervised learning", "unsupervised learning", "few-shot learning", "transfer learning"]
ai_models = ["bert", "gpt", "transformer", "llama", "resnet", "yolo", "random forest", "svm", "decision tree", "autoencoder"]
ai_tasks = ["ner", "relation extraction", "named entity recognition", "text classification", "medical imaging", "disease prediction", "drug discovery", "object detection", "anomaly detection"]
malware = ["emotet", "zeus", "ransomware", "trojan", "darkside", "wannacry", "stuxnet", "ryuk", "botnet", "rootkit"]
cyber_attacks = ["phishing", "ddos", "sql injection", "cross site scripting", "man in the middle", "brute force", "zero day", "privilege escalation"]
technologies = ["network traffic", "server", "database", "windows", "linux", "healthcare", "hospital system", "cloud", "iot", "router", "endpoint"]
security_tools = ["ids", "firewall", "antivirus", "siem", "edr", "vpn", "waf", "xdr", "mdm"]

# Specific prefixes for diverse generation
prefixes = {
    "Wikipedia": [
        "{} is widely recognized as a pivotal component.",
        "According to experts, {} can be utilized effectively.",
        "History shows that {} became mainstream recently.",
        "A standard implementation of {} involves multiple layers.",
        "Researchers note that {} is fundamental to the field.",
        "The architecture of {} provides significant advantages.",
        "{} is often contrasted with older legacy systems.",
        "In modern environments, {} is standard practice."
    ],
    "arXiv Papers": [
        "In this paper, we propose a novel approach using {}.",
        "Our experiments with {} demonstrate superior accuracy.",
        "We evaluate the theoretical limits of {} under pressure.",
        "The methodology focuses on integrating {}.",
        "State-of-the-art results were achieved by applying {}.",
        "We formalized the objective function for {}.",
        "Empirical evidence suggests that {} outperforms baselines.",
        "Ablation studies confirm the necessity of {}."
    ],
    "News": [
        "Breaking: Investigators trace the incident back to {}.",
        "Tech giants are heavily investing in {} this quarter.",
        "A critical alert was issued regarding {} today.",
        "Security researchers have discovered a flaw in {}.",
        "Market analysts predict massive growth for {}.",
        "The recent breach highlights the dangers of {}.",
        "Experts warn that {} could be highly disruptive.",
        "A new consortium was formed to standardize {}."
    ]
}

# Templates combining AI and Sec
templates = [
    "{ai_method} detects {malware} accurately.",
    "A custom {ai_model} prevents {cyber_attack} automatically.",
    "The {security_tool} analyzed the {technology} logs.",
    "{cyber_attack} often targets {technology} databases.",
    "{malware} spreads via {cyber_attack}.",
    "We used {ai_method} for {ai_task}.",
    "The {ai_model} is designed for {ai_task}.",
    "An outdated {technology} is vulnerable to {malware}.",
    "The {security_tool} blocked the {malware} effectively.",
    "Using {ai_model}, the system stopped the {cyber_attack}."
]

def generate_large_corpus(source: str, topic: str, scale_factor: int = 1000) -> list:
    """
    Generates a massive corpus of text for a specific topic to simulate
    fetching all available data for the dataset selection.
    Scale factor determines how many raw sentences are returned.
    """
    source_key = source if source in prefixes else "Wikipedia"
    source_prefixes = prefixes[source_key]
    
    sentences = []
    
    # Generate 10% exactly referencing the topic explicitly
    for _ in range(int(scale_factor * 0.1)):
        prefix = random.choice(source_prefixes).format(topic)
        sentences.append(prefix)
        
    # Generate 90% relational context
    for _ in range(int(scale_factor * 0.9)):
        template = random.choice(templates)
        
        sentence = template.format(
            ai_method=random.choice(ai_methods),
            ai_model=random.choice(ai_models),
            ai_task=random.choice(ai_tasks),
            malware=random.choice(malware),
            cyber_attack=random.choice(cyber_attacks),
            technology=random.choice(technologies),
            security_tool=random.choice(security_tools)
        )
        
        # Optionally prepend a source-style prefix
        if random.random() > 0.5:
             # Just use generic 'it' or 'the system' for the prefix subject 
             prefix = random.choice(source_prefixes).format("The system")
             sentence = f"{prefix} {sentence}"
             
        sentences.append(sentence)
        
    random.shuffle(sentences)
    return sentences

def fetch_data_from_source(source: str, topic: str, num_articles: int = 5):
    """
    Overridden to generate massive amounts of data. 
    num_articles acts as a multiplier (e.g. 5 articles = 5000 sentences).
    """
    print(f"Generating massive context for {source}: {topic}")
    return generate_large_corpus(source, topic, scale_factor=num_articles * 1000)
