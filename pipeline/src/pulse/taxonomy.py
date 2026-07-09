"""The skill taxonomy: canonical skills, their families, and alias patterns.

Deterministic on purpose — no LLM in the extraction path, so results are
reproducible, testable, and free. Patterns are compiled case-insensitively and
must handle the classic traps: Go vs "go", C vs C++ vs C#, R as a bare letter,
Java vs JavaScript, .NET's leading dot.

Each entry: slug -> (display name, family, regex pattern).
Families: language, frontend, backend, data, cloud, devops, ai, practice.
"""
from __future__ import annotations

import re

# NOTE ON PATTERNS
# - \b does not work after '+' or '#', so C++/C# use lookarounds.
# - "Go" and "R" only count with a strong disambiguator (e.g. "Go developer",
#   "in R,") — bare words are far too noisy in prose.
# - Java must not match JavaScript; JS aliases must not match "json".
TAXONOMY: dict[str, tuple[str, str, str]] = {
    # --- languages -----------------------------------------------------------
    "python":     ("Python", "language", r"\bpython\b"),
    "java":       ("Java", "language", r"\bjava\b(?!\s*script)"),
    "javascript": ("JavaScript", "language", r"\bjava\s*script\b|\bjs\b(?!on)"),
    "typescript": ("TypeScript", "language", r"\btype\s*script\b|\bts\b(?=[\s,./)]|$)"),
    "csharp":     ("C#", "language", r"c#|\bc\s*sharp\b|(?<![\w+])c#"),
    "cpp":        ("C++", "language", r"c\+\+"),
    "c-lang":     ("C", "language", r"\bc\b(?=\s*(?:/|,|and)\s*c\+\+)|\bembedded\s+c\b"),
    "golang":     ("Go", "language", r"\bgolang\b|\bgo\b(?=\s+(?:developer|engineer|programming|experience|microservices|services|lang\b))"),
    "rust":       ("Rust", "language", r"\brust\b"),
    "kotlin":     ("Kotlin", "language", r"\bkotlin\b"),
    "swift":      ("Swift", "language", r"\bswift\b(?!\s*(?:code|ly))"),
    "ruby":       ("Ruby", "language", r"\bruby\b"),
    "php":        ("PHP", "language", r"\bphp\b"),
    "scala":      ("Scala", "language", r"\bscala\b(?!bility)"),
    "r-lang":     ("R", "language", r"\br\b(?=\s*(?:programming|language|studio|/python|,\s*python|\s+and\s+python))|\bin\s+r\b(?=[\s,.;])"),
    "sql":        ("SQL", "language", r"\bsql\b(?!\s*server)|\bt-sql\b|\bpl/?sql\b"),
    "bash":       ("Bash/Shell", "language", r"\bbash\b|\bshell\s+script"),
    "matlab":     ("MATLAB", "language", r"\bmatlab\b"),

    # --- frontend ------------------------------------------------------------
    "react":      ("React", "frontend", r"\breact(?:\.?js)?\b(?!\s*native)"),
    "react-native": ("React Native", "frontend", r"\breact\s*native\b"),
    "nextjs":     ("Next.js", "frontend", r"\bnext\.?js\b"),
    "angular":    ("Angular", "frontend", r"\bangular(?:js)?\b"),
    "vue":        ("Vue", "frontend", r"\bvue(?:\.?js)?\b"),
    "html-css":   ("HTML/CSS", "frontend", r"\bhtml\b|\bcss\b"),
    "tailwind":   ("Tailwind", "frontend", r"\btailwind\b"),
    "flutter":    ("Flutter", "frontend", r"\bflutter\b"),

    # --- backend -------------------------------------------------------------
    "nodejs":     ("Node.js", "backend", r"\bnode\.?js\b|\bnodejs\b"),
    "dotnet":     (".NET", "backend", r"\.net\b|\bdot\s*net\b|\basp\.net\b"),
    "spring":     ("Spring", "backend", r"\bspring\s*(?:boot|framework)\b"),
    "django":     ("Django", "backend", r"\bdjango\b"),
    "fastapi":    ("FastAPI", "backend", r"\bfast\s*api\b"),
    "flask":      ("Flask", "backend", r"\bflask\b"),
    "rails":      ("Rails", "backend", r"\bruby\s+on\s+rails\b|\brails\b"),
    "laravel":    ("Laravel", "backend", r"\blaravel\b"),
    "graphql":    ("GraphQL", "backend", r"\bgraphql\b"),
    "rest-api":   ("REST APIs", "backend", r"\brest(?:ful)?\s*api"),
    "microservices": ("Microservices", "backend", r"\bmicro\s*services?\b"),

    # --- data ----------------------------------------------------------------
    "postgres":   ("PostgreSQL", "data", r"\bpostgres(?:ql)?\b"),
    "mysql":      ("MySQL", "data", r"\bmysql\b"),
    "sqlserver":  ("SQL Server", "data", r"\bsql\s*server\b|\bmssql\b"),
    "mongodb":    ("MongoDB", "data", r"\bmongo\s*db?\b"),
    "redis":      ("Redis", "data", r"\bredis\b"),
    "elasticsearch": ("Elasticsearch", "data", r"\belastic\s*search\b"),
    "kafka":      ("Kafka", "data", r"\bkafka\b"),
    "spark":      ("Spark", "data", r"\b(?:apache\s+)?spark\b"),
    "hadoop":     ("Hadoop", "data", r"\bhadoop\b"),
    "airflow":    ("Airflow", "data", r"\bairflow\b"),
    "dbt":        ("dbt", "data", r"\bdbt\b"),
    "snowflake":  ("Snowflake", "data", r"\bsnowflake\b"),
    "databricks": ("Databricks", "data", r"\bdatabricks\b"),
    "bigquery":   ("BigQuery", "data", r"\bbig\s*query\b"),
    "redshift":   ("Redshift", "data", r"\bredshift\b"),
    "tableau":    ("Tableau", "data", r"\btableau\b"),
    "powerbi":    ("Power BI", "data", r"\bpower\s*bi\b"),
    "etl":        ("ETL/ELT", "data", r"\betl\b|\belt\b(?=[\s,./)]|$)|\bdata\s+pipeline"),
    "pandas":     ("pandas", "data", r"\bpandas\b"),
    "numpy":      ("NumPy", "data", r"\bnumpy\b"),

    # --- cloud ---------------------------------------------------------------
    "aws":        ("AWS", "cloud", r"\baws\b|\bamazon\s+web\s+services\b"),
    "azure":      ("Azure", "cloud", r"\bazure\b"),
    "gcp":        ("Google Cloud", "cloud", r"\bgcp\b|\bgoogle\s+cloud\b"),
    "lambda":     ("Serverless", "cloud", r"\bserverless\b|\blambda\b"),
    "s3":         ("S3", "cloud", r"\bs3\b"),

    # --- devops --------------------------------------------------------------
    "docker":     ("Docker", "devops", r"\bdocker\b"),
    "kubernetes": ("Kubernetes", "devops", r"\bkubernetes\b|\bk8s\b"),
    "terraform":  ("Terraform", "devops", r"\bterraform\b"),
    "ansible":    ("Ansible", "devops", r"\bansible\b"),
    "jenkins":    ("Jenkins", "devops", r"\bjenkins\b"),
    "github-actions": ("GitHub Actions", "devops", r"\bgithub\s+actions\b"),
    "gitlab-ci":  ("GitLab CI", "devops", r"\bgitlab\b"),
    "cicd":       ("CI/CD", "devops", r"\bci/?cd\b|\bcontinuous\s+(?:integration|delivery|deployment)\b"),
    "linux":      ("Linux", "devops", r"\blinux\b|\bunix\b"),
    "git":        ("Git", "devops", r"\bgit\b(?!hub|lab)"),
    "grafana":    ("Grafana/Prometheus", "devops", r"\bgrafana\b|\bprometheus\b"),
    "datadog":    ("Datadog", "devops", r"\bdatadog\b"),
    "splunk":     ("Splunk", "devops", r"\bsplunk\b"),

    # --- ai ------------------------------------------------------------------
    "machine-learning": ("Machine Learning", "ai", r"\bmachine\s+learning\b|\bml\b(?=[\s,./)]|$)"),
    "deep-learning": ("Deep Learning", "ai", r"\bdeep\s+learning\b|\bneural\s+network"),
    "nlp":        ("NLP", "ai", r"\bnlp\b|\bnatural\s+language\s+processing\b"),
    "computer-vision": ("Computer Vision", "ai", r"\bcomputer\s+vision\b"),
    "llm":        ("LLMs / GenAI", "ai", r"\bllms?\b|\blarge\s+language\s+model|\bgen(?:erative)?\s*ai\b|\bgpt\b|\bchatgpt\b|\bopenai\b|\banthropic\b|\bclaude\b|\bgemini\b|\bcopilot\b"),
    "rag":        ("RAG", "ai", r"\brag\b(?=[\s,./)]|$)|\bretrieval[- ]augmented\b|\bvector\s+(?:database|db|search|store)\b"),
    "tensorflow": ("TensorFlow", "ai", r"\btensor\s*flow\b"),
    "pytorch":    ("PyTorch", "ai", r"\bpy\s*torch\b"),
    "sklearn":    ("scikit-learn", "ai", r"\bscikit[- ]?learn\b|\bsklearn\b"),
    "langchain":  ("LangChain", "ai", r"\blang\s*chain\b"),
    "mlops":      ("MLOps", "ai", r"\bml\s*ops\b"),

    # --- practices -----------------------------------------------------------
    "agile":      ("Agile/Scrum", "practice", r"\bagile\b|\bscrum\b|\bkanban\b"),
    "tdd":        ("Testing/TDD", "practice", r"\btdd\b|\bunit\s+test|\btest[- ]driven\b|\bpytest\b|\bjest\b|\bplaywright\b|\bselenium\b|\bcypress\b"),
    "security":   ("Security", "practice", r"\bcyber\s*security\b|\bappsec\b|\bpenetration\s+test|\bowasp\b|\binfosec\b"),
    "api-design": ("System Design", "practice", r"\bsystem\s+design\b|\bdistributed\s+systems?\b"),
}

COMPILED: dict[str, re.Pattern] = {
    slug: re.compile(pattern, re.IGNORECASE) for slug, (_, _, pattern) in TAXONOMY.items()
}


def seed_rows() -> list[tuple[str, str, str]]:
    """(slug, display, family) rows for the skills table."""
    return [(slug, display, family) for slug, (display, family, _) in TAXONOMY.items()]
