tool_catalog = {
    # --- Alignment + Structure ---
    "check_alignment": {
        "version": "1.0",
        "description": "Checks if proposal aligns with goals, requirements, or evaluation criteria.",
        "usage": 'check_alignment["modular EHR platform aligns with scalability needs"]',
        "examples": [
            'check_alignment["timeline aligns with phased rollout for primary care clinics"]'
        ]
    },
    "highlight_missing_sections": {
        "version": "1.0",
        "description": "Flags missing key sections like costs, risks, methodology, or team.",
        "usage": "highlight_missing_sections",
        "examples": [
            'highlight_missing_sections["The proposal lacks a detailed risk management plan."]'
        ]
    },
    "keyword_match": {
        "version": "1.0",
        "description": "Performs keyword-level match to assess coverage of key topics.",
        "usage": 'keyword_match["privacy compliance"]',
        "examples": [
            'keyword_match["data privacy compliance"]'
        ]
    },
    "check_summary_support": {
        "version": "1.0",
        "description": "Validates whether recommendations are clearly supported by the proposal content.",
        "usage": "check_summary_support",
        "examples": [
            'check_summary_support["The vendor has a strong track record in healthcare."]'
        ]
    },
    "check_section_structure": {
        "version": "1.0",
        "description": "Checks for logical structure, headings, and section flow.",
        "usage": "check_section_structure",
        "examples": [
            'check_section_structure["The proposal is organized into clear sections with headings."]'
        ]
    },

    # --- Methodology + Delivery Lifecycle ---
    "check_agile_compatibility": {
        "version": "1.0",
        "description": "Checks if agile is used in a structured, client-compatible way (e.g. agile with fixed price).",
        "usage": 'check_agile_compatibility["We use agile with fixed-price milestones and client-approved sprints."]',
        "examples": [
            'check_agile_compatibility["Our agile approach is structured with upfront planning, sprint-based delivery, and cost tracking tied to deliverables."]'
        ]
    },
    "check_accelerators_and_tools": {
        "version": "1.0",
        "description": "Checks for use of accelerators, templates, or proprietary tools to improve delivery.",
        "usage": 'check_accelerators_and_tools["We use our proven set of templates and automation tools for rapid deployment."]',
        "examples": [
            'check_accelerators_and_tools["Our proprietary DevOps toolchain automates testing, code review, and deployment with standardized playbooks."]'
        ]
    },
    "evaluate_collaboration_approach": {
        "description": "Evaluates whether the proposal's team or delivery model promotes a strong, collaborative partnership.",
        "usage": 'evaluate_collaboration_approach["team or delivery section text"]',
        "version": "1.0",
        "examples": [
            'evaluate_collaboration_approach["Our team will work in daily stand-ups with the client team."]'
        ]
    },
    "check_discovery_approach": {
    "version": "1.0",
    "description": "Evaluates whether the Discovery phase methodology is clear, structured, and stakeholder-driven.",
    "usage": 'check_discovery_approach["Discovery will begin with stakeholder interviews and current state assessment."]',
    "examples": [
        'check_discovery_approach["Our discovery approach includes stakeholder workshops, baseline capability assessment, and early risk identification."]'
    ]
    },
    "check_requirements_approach": {
        "version": "1.0",
        "description": "Evaluates the vendor’s method for gathering and managing requirements.",
        "usage": 'check_requirements_approach["We gather requirements via workshops and trace them to solution components."]',
        "examples": [
            'check_requirements_approach["We use user stories, process mapping, and MoSCoW prioritization with business and technical stakeholders."]'
        ]
    },
    "check_design_approach": {
        "version": "1.0",
        "description": "Assesses whether the vendor’s design phase addresses UX, integration, architecture, and collaboration.",
        "usage": 'check_design_approach["We use iterative design with wireframes and architecture review boards."]',
        "examples": [
            'check_design_approach["System design includes technical diagrams, UX prototyping, security review, and traceability to requirements."]'
        ]
    },
    "check_build_approach": {
        "version": "1.0",
        "description": "Evaluates the vendor’s approach to the Build phase including agile practices, reuse, quality, and documentation.",
        "usage": 'check_build_approach["We will develop using agile sprints and DevSecOps practices."]',
        "examples": [
            'check_build_approach["Development will follow agile iterations, with automated code checks, daily standups, and CI/CD pipelines."]'
        ]
    },
    "check_test_approach": {
        "version": "1.0",
        "description": "Assesses whether the testing approach includes automation, accessibility, performance, and client involvement.",
        "usage": 'check_test_approach["We will conduct UAT and regression testing using automation tools and JIRA tracking."]',
        "examples": [
            'check_test_approach["Our test strategy includes unit, system, integration, and UAT, supported by automation frameworks and traceability to requirements."]'
        ]
    },
    "check_deployment_approach": {
        "version": "1.0",
        "description": "Evaluates the vendor’s go-live planning including cutover, readiness, communication, and rollback strategy.",
        "usage": 'check_deployment_approach["We use a phased rollout with go/no-go gates and rollback procedures."]',
        "examples": [
            'check_deployment_approach["Deployment includes stakeholder training, communication plan, and rollback strategy."]'
        ]
    },
    "check_operate_approach": {
        "version": "1.0",
        "description": "Assesses the vendor’s sustainment model, including SLAs, incident management, monitoring, and continuous improvement.",
        "usage": 'check_operate_approach["Post-deployment support includes SLAs, incident tracking, and quarterly feedback reviews."]',
        "examples": [
            'check_operate_approach["We offer 24x7 support, monthly reports, continuous feedback collection, and enhancement sprints."]'
        ]
    },

    # --- Team + Resources ---
    "check_team_experience_alignment": {
        "description": "Evaluates if the proposed team has the required experience and qualifications for the project.",
        "usage": "check_team_experience_alignment[section text]",
        "examples": [
            'check_team_experience_alignment["Our project manager has 20 years of experience in public sector digital health projects..."]',
            'check_team_experience_alignment["The proposed development team has worked on multiple EHR implementations across North America..."]'
        ],
        "version": "v1"
    },
    "detect_bait_and_switch_risk": {
        "description": "Identifies signs that the proposed team may not be the one actually staffed on the project.",
        "usage": "detect_bait_and_switch_risk[section text]",
        "examples": [
            'detect_bait_and_switch_risk["We will provide qualified team members at the appropriate time during implementation."]',
            'detect_bait_and_switch_risk["Exact individuals to be confirmed post-award, depending on availability."]'
        ],
        "version": "v1"
    },

    "check_local_resource_presence": {
        "description": "Checks if vendor proposes to use local/on-site resources, which clients often value.",
        "usage": "check_local_resource_presence[section text]",
        "examples": [
            'check_local_resource_presence["Our team will be based in Toronto and will work from the client’s office 3 days per week."]',
            'check_local_resource_presence["Key resources will work remotely, with travel to client site only as needed."]'
        ],
        "version": "v1"
    },

    # --- Vendor Experience ---
    "check_vendor_experience_relevance": {
        "description": "Evaluates whether the vendor demonstrates experience with similar scale, scope, or domain.",
        "usage": 'check_vendor_experience_relevance["<section text>"]',
        "version": "1.0",
        "examples": [
            'check_vendor_experience_relevance["We deployed our platform across 12 regional health networks..."]'
        ]
    },
    "check_vendor_experience_evidence": {
        "description": "Checks for concrete evidence of vendor experience, such as client names, success metrics, or case studies.",
        "usage": 'check_vendor_experience_evidence["<section text>"]',
        "version": "1.0",
        "examples": [
            'check_vendor_experience_evidence["Client success: Reduced hospital readmission rates by 18%..."]'
        ]
    },

    # --- Implementation Plan ---
    "check_implementation_milestones": {
        "description": "Checks if implementation milestones and phases are clearly outlined.",
        "usage": "check_implementation_milestones[section_text]",
        "version": "1.0",
        "examples": [
            'check_implementation_milestones["The project will follow a phased approach including onboarding, integration, testing, and go-live."]'
        ]
    },
    "check_resource_plan_realism": {
        "description": "Evaluates whether the proposed resource plan is realistic for the work described.",
        "usage": "check_resource_plan_realism[section_text]",
        "version": "1.0",
        "examples": [
            'check_resource_plan_realism["We will assign one project manager and four developers for a 12-month nationwide rollout."]'
        ]
    },
    "check_assumption_reasonableness": {
        "description": "Evaluates whether the stated assumptions in the proposal are reasonable.",
        "usage": "check_assumption_reasonableness[section_text]",
        "version": "1.0",
        "examples": [
            'check_assumption_reasonableness["We assume all data will be clean, structured, and available via API on day one."]'
        ]
    },
    "check_timeline_feasibility": {
        "version": "1.0",
        "description": "Evaluates whether the proposed timeline is reasonable.",
        "usage": 'check_timeline_feasibility["The project will be completed in 12 weeks."]',
        "examples": [
            'check_timeline_feasibility["The implementation is expected to take 18 months with phases including design, development, testing, and rollout."]'
        ]
    },
    "check_contingency_plans": {
        "version": "1.0",
        "description": "Evaluates risk and fallback planning in case of delays or issues.",
        "usage": 'check_contingency_plans["In case of delay, we will adjust testing timelines and increase staffing to maintain go-live."]',
        "examples": [
            'check_contingency_plans["We will maintain a risk log and have weekly project health check-ins to identify mitigation options early."]'
        ]
    },



    # --- Cost + Value ---
    "analyze_cost_structure": {
        "version": "1.0",
        "description": "Breaks down cost types: fixed price, subscription, rate cards.",
        "usage": "analyze_cost_structure"
    },
    "check_value_for_money": {
        "version": "1.0",
        "description": "Evaluates whether the proposed price is reasonable given what's being offered.",
        "usage": 'check_value_for_money["The platform costs $500K and includes hosting, support, and training."]',
        "examples": [
            'check_value_for_money["The platform costs $2M upfront and $200K per year. It includes minimal support."]'
        ]
    },
    "check_cost_benchmark": {
        "version": "1.0",
        "description": "Compares proposed pricing against typical vendor pricing for similar solutions.",
        "usage": 'check_cost_benchmark["The vendor proposes $15/user/month for access to all modules."]',
        "examples": [
            'check_cost_benchmark["$500K onboarding fee with $100/user/month for core access."]'
        ]
    },
    "generate_cost_forecast": {
        "version": "1.0",
        "description": "Forecasts total cost exposure based on pricing and risk factors.",
        "usage": 'generate_cost_forecast["$20/user/month, with client responsible for training and data migration."]',
        "examples": [
            'generate_cost_forecast["Pricing is based on tiered volume, with annual escalators and optional modules."]'
        ]
    },

    # --- Risk Management ---
    "check_data_privacy_and_security_measures": {
        "version": "1.0",
        "description": "Evaluates the presence and quality of data privacy and security protections.",
        "usage": 'check_data_privacy_and_security_measures["Data is encrypted and hosted in a compliant cloud."]',
        "examples": [
            'check_data_privacy_and_security_measures["SOC 2 certified, HIPAA compliant, role-based access control."]'
        ]
    },
    "check_risk_register_or_mitigation_plan": {
        "version": "1.0",
        "description": "Checks for a clear risk register or mitigation strategy.",
        "usage": 'check_risk_register_or_mitigation_plan["The vendor identifies integration delays and provides fallback options."]',
        "examples": [
            'check_risk_register_or_mitigation_plan["Risks are captured in a matrix with probability and impact."]'
        ]
    },
    "check_compliance_certifications": {
        "version": "1.0",
        "description": "Checks for security and compliance certifications such as ISO, SOC 2, HIPAA.",
        "usage": 'check_compliance_certifications["The solution is ISO 27001 and SOC 2 Type II certified."]',
        "examples": [
            'check_compliance_certifications["HIPAA compliant, verified annually by third party audit."]'
        ]
    },


    # --- Solution Fit ---
    "evaluate_product_fit": {
        "version": "1.0",
        "description": "Checks alignment of product functionality with requirements.",
        "usage": 'evaluate_product_fit["Our platform automates intake and scheduling."]',
        "examples": [
            'evaluate_product_fit["Supports real-time patient lookup and appointment routing."]'
        ]
    },
    "evaluate_nfr_support": {
        "version": "1.0",
        "description": "Checks for support of privacy, security, UX, accessibility, performance, etc.",
        "usage": 'evaluate_nfr_support["We use AES-256 encryption, WCAG 2.1 AA-compliant interfaces, and SLA-backed uptime."]',
        "examples": [
            'evaluate_nfr_support["Data is encrypted and access is role-restricted."]'
        ]
    },
    "evaluate_modularity_and_scalability": {
        "version": "1.0",
        "description": "Evaluates product adaptability, modularity, and scale potential.",
        "usage": 'evaluate_modularity_and_scalability["Modules can be independently deployed and scaled across regions."]',
        "examples": [
            'evaluate_modularity_and_scalability["Supports multi-tenant deployments and horizontal scaling."]'
        ]
    },
    "check_product_roadmap": {
        "version": "1.0",
        "description": "Checks future investment and evolution of the product.",
        "usage": 'check_product_roadmap["Roadmap includes support for AI triage, real-time collaboration, and national integration."]',
        "examples": [
            'check_product_roadmap["We plan to add predictive analytics and FHIR-native APIs in 2025."]'
        ]
    },
    "evaluate_demos_and_proofs": {
        "version": "1.0",
        "description": "Looks at demos, pilots, and referenced outcomes.",
        "usage": 'evaluate_demos_and_proofs["Demonstration videos and two provincial case studies are included."]',
        "examples": [
            'evaluate_demos_and_proofs["Outcome: reduced call handling time by 30% in pilot deployment."]'
        ]
    },

    # --- Meta / Utility ---
    "suggest_tool_for": {
        "version": "1.0",
        "description": "Suggests which tool(s) to use based on your goal.",
        "usage": 'suggest_tool_for["evaluate scalability of product"]',
        "examples": [
            'suggest_tool_for["evaluate scalability of product"]'
        ]
    },
    "tool_help": {
        "version": "1.0",
        "description": "Returns help and examples for the named tool.",
        "usage": 'tool_help["check_assumptions_validity"]',
        "examples": [
            'tool_help["check_assumptions_validity"]'
        ]
    },
    "auto_fill_gaps_with_research": {
        "version": "1.0",
        "description": "Fills vague content with relevant external evidence.",
        "usage": 'auto_fill_gaps_with_research["data privacy best practices"]',
        "examples": [
            'auto_fill_gaps_with_research["data privacy best practices"]'
        ]
    },
    "check_guideline_dynamic": {
        "version": "1.0",
        "description": "Searches for industry standards/guidelines on a topic.",
        "usage": 'check_guideline_dynamic["FHIR security best practices"]',
        "examples": [
            'check_guideline_dynamic["FHIR security best practices"]'
        ]
    },
    "detect_boilerplate_or_marketing_fluff": {
        "description": "Identifies vague or overly promotional content in a proposal section.",
        "usage": 'detect_boilerplate_or_marketing_fluff["section text"]',
        "version": "1.0",
        "examples": [
            'detect_boilerplate_or_marketing_fluff["We deliver world-class value with seamless integration."]'
        ]
    },
    "evaluate_writing_clarity": {
        "description": "Provides feedback on the clarity, conciseness, and readability of the proposal section.",
        "usage": 'evaluate_writing_clarity["section text"]',
        "version": "1.0",
        "examples": [
            'evaluate_writing_clarity["Our unique approach leverages synergies across the ecosystem."]'
        ]
    },
    "check_fact_substantiation": {
        "description": "Assesses whether proposal claims are backed by evidence or examples.",
        "usage": 'check_fact_substantiation["text to check"]',
        "version": "1.0",
        "examples": [
            'check_fact_substantiation["We have extensive experience in the healthcare sector."]'
        ]
    },
    "check_for_unsupported_assumptions": {
        "description": "Finds assumptions in the proposal and flags those that may be unrealistic or risky.",
        "usage": 'check_for_unsupported_assumptions["proposal section text"]',
        "version": "1.0",
        "examples": [
            'check_for_unsupported_assumptions["Client will provide integration team and data migration tools."]'
        ]
    }
}


