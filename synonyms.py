DOMAIN_SYNONYMS = {
    "python": {"py", "python3", "python programming"},
    "java": {"java8", "j2ee"},
    "sql": {"mysql", "postgres", "structured query language"},
    "pytorch": {"torch", "deep learning framework"},
    "tensorflow": {"tf", "keras"},
    "react": {"reactjs", "react.js"},
    "fastapi": {"api development", "rest api"},
    "docker": {"container", "containerization"},
    "kubernetes": {"k8s", "container orchestration"},
    "aws": {"amazon web services", "ec2", "s3", "lambda"},
    "gcp": {"google cloud", "bigquery", "vertex ai"},
    "azure": {"microsoft azure", "azure ml"},
    "airflow": {"workflow orchestration", "etl pipeline"},
    "spark": {"pyspark", "big data processing"},
    "kafka": {"streaming", "pubsub", "real-time pipeline"},
    "machine learning": {"ml", "predictive modeling", "data modeling"},
    "deep learning": {"neural networks", "representation learning"},
    "nlp": {"natural language processing", "text mining"},
    "computer vision": {"image recognition", "object detection"},
    "data visualization": {"dashboard", "plotting", "charting"},
    "data analysis": {"exploratory data analysis", "eda"},
    "mlops": {"model deployment", "ci cd for ml", "ml lifecycle"},
    "communication": {"presentation", "public speaking", "writing"},
    "leadership": {"team management", "mentoring"},
    "cross functional": {"multidisciplinary", "interdisciplinary"},
    "gdpr": {"data privacy law"},
    "hipaa": {"health data compliance"},
}

# Normalize
DOMAIN_SYNONYMS = {
    k.lower(): {v.lower() for v in vals} | {k.lower()}
    for k, vals in DOMAIN_SYNONYMS.items()
}