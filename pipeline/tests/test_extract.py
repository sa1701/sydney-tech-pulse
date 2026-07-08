"""Extractor tests — the classic false-positive traps, pinned forever."""
from pulse.extract import extract_skills


def test_java_does_not_match_javascript():
    skills = extract_skills("Strong JavaScript and TypeScript experience")
    assert "javascript" in skills
    assert "typescript" in skills
    assert "java" not in skills


def test_java_matches_alone():
    assert "java" in extract_skills("5+ years Java and Spring Boot")


def test_js_alias_does_not_match_json():
    assert "javascript" not in extract_skills("Parse JSON payloads from the API")


def test_go_needs_disambiguator():
    assert "golang" not in extract_skills("go to market strategy, willingness to go far")
    assert "golang" in extract_skills("Backend services written in Golang")
    assert "golang" in extract_skills("experienced Go developer wanted")


def test_c_family_disambiguation():
    text = "Systems programming in C/C++ and C# for tooling"
    skills = extract_skills(text)
    assert "cpp" in skills
    assert "csharp" in skills
    assert "c-lang" in skills


def test_c_not_matched_in_prose():
    assert "c-lang" not in extract_skills("Grade C driving licence required")


def test_r_needs_context():
    assert "r-lang" not in extract_skills("Contact R Smith for details")
    assert "r-lang" in extract_skills("Statistical modelling in R programming")
    assert "r-lang" in extract_skills("proficiency in R, Python and SQL" )


def test_dotnet_leading_dot():
    assert "dotnet" in extract_skills("Full-stack development with .NET and Azure")


def test_react_native_vs_react():
    only_native = extract_skills("Build mobile apps with React Native")
    assert "react-native" in only_native
    assert "react" not in only_native
    assert "react" in extract_skills("SPA development in React.js")


def test_scala_not_scalability():
    assert "scala" not in extract_skills("Focus on scalability and reliability")
    assert "scala" in extract_skills("Data engineering in Scala and Spark")


def test_ml_abbreviation_boundaries():
    assert "machine-learning" in extract_skills("Experience with ML pipelines")
    assert "machine-learning" not in extract_skills("html templates")


def test_common_stack_sentence():
    text = ("Graduate engineer: Python, AWS (Lambda, S3), Docker, Kubernetes, "
            "PostgreSQL, CI/CD with GitHub Actions, and RAG/LLM experience.")
    skills = extract_skills(text)
    for expected in ("python", "aws", "lambda", "s3", "docker", "kubernetes",
                     "postgres", "cicd", "github-actions", "rag", "llm"):
        assert expected in skills, expected


def test_empty_and_none_safe():
    assert extract_skills("") == set()
    assert extract_skills(None) == set()
