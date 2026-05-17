// ============================================================
// SINGLE SOURCE OF TRUTH — update here, everything else syncs
// ============================================================
const resumeData = {

  name: "Jatin Patware",
  title: "Senior Data Engineer",
  tagline1: "Transforming Raw Data into Competitive Advantage.",
  tagline2: "Designing data systems that scale.",
  sub: "8+ Years · Petabyte Scale · Real-Time Pipelines · AI/LLM Integration",
  location: "Hyderabad, India",
  email: "jatincse19@gmail.com",
  linkedin: "https://linkedin.com/in/jatin-patware-b9411183",
  github: "https://github.com/jatinpatware",
  portfolio: "https://jatinpatware.github.io",
  credly: "https://www.credly.com/users/jatin-patware.02075313",

  heroBadges: [
    "Apache Spark", "Kafka Streams", "AWS", "Apache Iceberg",
    "Data Mesh", "LLM Integration", "Scala", "Python", "Airflow", "Snowflake"
  ],

  summary: `Data Engineer with 8+ years of experience known for strong system design instincts
    and structured logical thinking — translating ambiguous business and infrastructure problems
    into clean, scalable data architectures. Experienced across the full data platform lifecycle:
    from requirements and design through to delivery, governance, and optimisation. Deep hands-on
    exposure to Apache Spark, AWS, and distributed pipeline design at petabyte scale. Currently at
    Fanatics, one of the world's largest licensed sports merchandise platforms. Equally comfortable
    whiteboarding a data mesh architecture, reviewing an engineer's design, or digging into a pipeline
    bottleneck. Experienced in mentoring engineers, driving cross-functional alignment, and integrating
    AI/LLM tooling into data workflows.`,

  focus: [
    "Clean data architecture from ambiguous requirements",
    "Pipeline performance — Spark UI and DAG debugging are second nature",
    "Data contracts and quality frameworks that prevent incidents",
    "LLM tooling integration to reduce engineering overhead",
    "Mentoring engineers and cross-functional technical alignment"
  ],

  skills: [
    { category: "Core", items: ["System Design", "Data Architecture", "Apache Spark", "Scala", "PySpark", "SQL", "Python", "Distributed Systems", "ETL / Pipeline Design", "Technical Mentoring"] },
    { category: "Cloud & Infra", items: ["AWS S3", "AWS EMR", "AWS Glue", "AWS Lambda", "AWS Redshift", "AWS Bedrock", "Azure ADF", "Azure Functions", "Azure HD Insights", "Snowflake", "Docker"] },
    { category: "Streaming", items: ["Apache Kafka", "Kafka Streams", "Event-driven Architecture", "Real-Time Processing"] },
    { category: "Storage & Query", items: ["Apache Iceberg", "Spark SQL", "Trino", "Hive", "Redshift", "S3 Data Lake", "Parquet", "ORC"] },
    { category: "Orchestration", items: ["Apache Airflow", "Stonebranch", "DAG Design", "Dependency Management"] },
    { category: "Data Platform", items: ["Data Mesh", "Data Contracts", "Data Lineage", "Data Quality Frameworks", "Data Cataloguing", "Data Governance", "SLA Management"] },
    { category: "AI / LLM", items: ["AWS Bedrock", "Bedrock Agents", "LLaMA3", "Glean", "Claude (Anthropic)", "MCP (Model Context Protocol)", "LLM Pipeline Integration", "Agentic Solutions", "Claude Code Skills"] },
    { category: "BI / Legacy", items: ["Power BI", "SSAS Tabular", "SSMS", "SSIS", "C#", "Stored Procedures"] },
    { category: "Engineering", items: ["CI/CD Pipelines", "Git", "Agile / Scrum", "MCP", "Glean Search", "System Design Reviews", "Performance Tuning", "Spark UI", "DAG Inspection"] }
  ],

  experience: [
    {
      company: "FANATICS E-COMMERCE (INDIA) LLP",
      companyDesc: "Global Licensed Sports Merchandise Platform",
      period: "Feb 2022 – Present",
      roles: [
        {
          title: "Senior Data Engineer",
          period: "Mar 2025 – Present",
          stack: "Apache Spark (Scala) · AWS (S3, EMR, Glue, Lambda, Bedrock) · Kafka Streams · Airflow · Stonebranch · Trino · Python · SQL · Docker",
          bullets: [
            "Own design and reliability of real-time order event processing on Kafka Streams — canonical data models and transformation contracts supporting <strong>30–40K messages/min at peak</strong> across multiple downstream consumers",
            "Maintain and evolve the canonical Iceberg layer at <strong>petabyte scale</strong>, consumed by downstream BI and analytics systems",
            "Built an <strong>agentic solution for automated order data lineage tracing</strong> across a complex multi-layer pipeline — enabling engineers to debug field discrepancies end-to-end across Kafka Streams, Iceberg, and downstream BI layers",
            "Integrated LLM-powered capabilities using AWS Bedrock Agents, Glean, and Claude — automated insight surfacing and reduced engineering overhead",
            "Mentored junior and mid-level engineers; go-to design reviewer across cross-functional squads",
            "Drove data mesh adoption — data contracts, lineage, and cataloguing at platform scale"
          ]
        },
        {
          title: "Data Engineer III",
          period: "Mar 2022 – Feb 2025",
          company: "FANATICS E-COMMERCE (INDIA) LLP",
          stack: "Apache Spark (Scala) · AWS (S3, EMR, Glue, Lambda) · Kafka Streams · Stonebranch · Trino · Python · SQL",
          bullets: [
            "Designed and delivered Spark batch pipelines on AWS processing petabyte-scale commerce data — significant runtime and compute cost reductions via Spark UI and DAG tuning",
            "Built backend data pipelines powering executive dashboards — enabling <strong>200+ ecommerce metrics</strong> consumed by senior leadership",
            "Designed and built an <strong>in-house data quality framework in Scala/Spark with YAML-based rule configuration</strong> — adopted across critical pipelines for validation, SLA enforcement, and alerting",
            "Built an <strong>LLM-powered executive insight engine</strong> (internal hackathon) — LLaMA3 on EC2, invoked via AWS Lambda, generating natural language insights from enriched S3 commerce data",
            "Built ETL pipelines in Scala/Spark powering BI reporting layers — translating raw commerce events into clean, reliable analytical datasets",
            "Owned orchestration across <strong>100+ workflows</strong> on Stonebranch — rationalised dependency graphs and standardised failure recovery approaches"
          ]
        }
      ]
    },
    {
      company: "Fractal Analytics",
      period: "Nov 2020 – Jan 2022",
      roles: [
        {
          title: "Data Engineer",
          period: "Nov 2020 – Jan 2022",
          stack: "Snowflake · Azure Data Factory · Python · SQL",
          bullets: [
            "Built ETL pipelines into Snowflake for Marketing Mix Modelling and Supply Chain analytics clients",
            "Created transformation and harmonisation layers across client datasets",
            "Worked across multiple client engagements with focus on pipeline reliability and data consistency"
          ]
        }
      ]
    },
    {
      company: "MAQ Software",
      period: "Jul 2018 – Oct 2020",
      roles: [
        {
          title: "BI & Backend Engineer",
          period: "Jul 2018 – Oct 2020",
          stack: "SSMS · SSAS · SQL · Azure Data Factory · Azure Functions · C# · Power BI · HD Insights",
          bullets: [
            "Developed enterprise BI solutions — tabular SSAS models, SSIS ETL pipelines, stored procedures, and Power BI dashboards",
            "Built Azure Functions for API ingestion and CI/CD pipelines for automated deployment"
          ]
        }
      ]
    }
  ],

  // featured: true = teal highlight; all certs in one flat list
  certifications: [
    { name: "AWS Certified Data Engineer – Associate",                icon: "☁️", featured: true, link: "https://cp.certmetrics.com/amazon/en/public/verify/credential/4fdc06a7d5484a28a7366cf8c0d0f1d7" },
    { name: "Microsoft Certified: Azure Data Engineer Associate",     icon: "🔷", link: "https://www.credly.com/badges/4736cbac-f9d1-4401-a170-0e1fd841889d/public_url" },
    { name: "Microsoft Certified: Azure Developer Associate",         icon: "🔷", link: "https://www.credly.com/badges/02f8ecf3-1692-4650-9512-54ddd4216f10/public_url" },
    { name: "MCSE: Data Management and Analytics (2019)",             icon: "🔷", link: "https://www.credly.com/badges/4a35bfc4-5c82-4b7d-b51c-8f7cb29204f0/public_url" },
    { name: "DP-200: Implementing an Azure Data Solution",            icon: "🔷", link: "https://www.credly.com/badges/b599c06b-6087-4c94-98b1-30d37b24eeb9/public_url" },
    { name: "DP-201: Designing an Azure Data Solution",               icon: "🔷", link: "https://www.credly.com/badges/9e072037-6fde-4af1-91b2-64d56ae5e08a/public_url" },
    { name: "Exam 778: Analyzing and Visualizing Data with Power BI", icon: "🔷", link: "https://www.credly.com/badges/8e2e759a-4ef2-4138-98de-765fa505f560/public_url" },
    { name: "Exam 761: Querying Data with Transact-SQL",              icon: "🔷", link: "https://www.credly.com/badges/111a5a1f-9e10-491d-80ed-72ac0017428d/public_url" },
    { name: "Exam 762: Developing SQL Databases",                     icon: "🔷", link: "https://www.credly.com/badges/8da646ce-10c4-4b06-b65c-856462065887/public_url" },
    { name: "Exam 768: Developing SQL Data Models",                   icon: "🔷", link: "https://www.credly.com/badges/306d9345-65e0-4253-af61-1b0fb85a779b/public_url" },
    { name: "Coursera: Data Structures & Algorithms Specialisation",  icon: "📘", link: "https://github.com/jatinpatware/Certifiacates" },
  ],

  // Set github: "https://github.com/jatinpatware/<repo>" when ready to publish
  projects: [
    // ── Professional (coming soon) ───────────────────────────────
    {
      name: "Data Quality Framework",
      desc: "Scala/Spark DQ framework with YAML-based rule configuration — covering validation, SLA enforcement, and alerting across batch pipelines.",
      stack: ["Scala", "Apache Spark", "YAML", "AWS"],
      status: "coming-soon",
      github: null
    },
    {
      name: "LLM Executive Insight Engine",
      desc: "LLM-powered insight engine — LLaMA3 on EC2, invoked via AWS Lambda, generating natural language insights from structured pipeline data.",
      stack: ["LLaMA3", "AWS Lambda", "EC2", "S3", "Python"],
      status: "coming-soon",
      github: null
    },
    {
      name: "Pipeline Lineage Tracer",
      desc: "Agentic tool for automated end-to-end data lineage tracing across a multi-layer streaming and batch pipeline — enabling engineers to debug field discrepancies without manual digging.",
      stack: ["Glean", "MCP", "Claude Code Skills", "Agentic AI"],
      status: "coming-soon",
      github: null
    },
    {
      name: "Portfolio as a Product",
      desc: "Open-source engineer portfolio template — single config file drives the site, resume, and README via CI/CD. Deploy to GitHub Pages in minutes. Built to be AI-assistant-agnostic.",
      stack: ["JavaScript", "GitHub Actions", "GitHub Pages", "CI/CD"],
      status: "coming-soon",
      github: null
    },
    // ── Academic / Open Source ───────────────────────────────────
    {
      name: "Algorithm Courses",
      desc: "C++ implementations of core data structures and algorithms — sorting, searching, graphs, dynamic programming, and tree traversals. Companion code for the Coursera DSA Specialisation.",
      stack: ["C++", "Data Structures", "Algorithms"],
      status: "live",
      academic: true,
      github: "https://github.com/jatinpatware/Algorithm-Courses"
    },
    {
      name: "Data Science",
      desc: "SQL-based data science experiments covering exploratory analysis, aggregations, window functions, and analytical query patterns.",
      stack: ["SQL", "Data Analysis"],
      status: "live",
      academic: true,
      github: "https://github.com/jatinpatware/Data-Science"
    },
    {
      name: "Data Warehousing & Mining",
      desc: "Academic implementations of data warehousing concepts and data mining algorithms — dimensional modelling, ETL patterns, and classification techniques.",
      stack: ["Data Warehousing", "Data Mining", "ETL"],
      status: "live",
      academic: true,
      github: "https://github.com/jatinpatware/Dataware_Housing_-_Mining"
    }
  ],

  education: [
    {
      degree: "M.Tech — Computer Science & Engineering",
      school: "National Institute of Technology Allahabad (MNNIT)",
      period: "2016 – 2018",
      cgpa: "8.55 / 10",
      notes: ["AIR-1518 in GATE 2016 (Computer Science)", "Co-ordinator, Data Analytics & ML Workshop (2017, 2018)"]
    },
    {
      degree: "B.E. — Computer Science & Engineering",
      school: "Madhav Institute of Technology & Science, Gwalior (MITS)",
      period: "2012 – 2016",
      cgpa: "7.8 / 10",
      notes: []
    }
  ],

  achievements: [
    "AIR-1518 in GATE 2016 (Computer Science)",
    "Recognised by management for autonomous problem-solving on a high-impact production project at Fanatics",
    "Co-ordinator, Data Analytics & ML Workshop at MNNIT (2017, 2018)"
  ]
};
