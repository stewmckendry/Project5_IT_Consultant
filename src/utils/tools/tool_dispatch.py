from src.utils.tools.tools_general import (
    detect_boilerplate_or_marketing_fluff,
    evaluate_writing_clarity,
    check_fact_substantiation,
    check_for_unsupported_assumptions
)

from src.utils.tools.tools_basic import check_guideline_dynamic

from src.utils.tools.tools_RFP_team import (
    check_team_experience_alignment,
    detect_bait_and_switch_risk,
    check_local_resource_presence
)

from src.utils.tools.tools_rfp_experience import (
    check_vendor_experience_relevance,
    check_vendor_experience_evidence
)

from src.utils.tools.tools_RFP_plan import (
    check_implementation_milestones,
    check_resource_plan_realism,
    check_assumption_reasonableness,
    check_timeline_feasibility,
    check_contingency_plans
)

from src.utils.tools.tools_rfp_method import (
    evaluate_collaboration_approach,
    check_discovery_approach,
    check_requirements_approach,
    check_design_approach,
    check_build_approach,
    check_test_approach,
    check_deployment_approach,
    check_operate_approach,
    check_agile_compatibility,
    check_accelerators_and_tools
)

from src.utils.tools.tools_RFP_costs import (
    check_value_for_money,
    check_cost_benchmark,
    generate_cost_forecast
)

from src.utils.tools.tools_RFP_risk import (
    check_data_privacy_and_security_measures,
    check_risk_register_or_mitigation_plan,
    check_compliance_certifications
)

from src.utils.tools.tools_RFP_fit import (
    evaluate_product_fit,
    evaluate_nfr_support,
    evaluate_modularity_and_scalability,
    check_product_roadmap,
    evaluate_demos_and_proofs
)

TOOL_FUNCTION_MAP = {
    # General Tools
    "check_guideline_dynamic": {
        "fn": check_guideline_dynamic,
        "args": ["agent", "input_arg"]
    },
    "detect_boilerplate_or_marketing_fluff": {
        "fn": detect_boilerplate_or_marketing_fluff,
        "args": ["agent", "input_arg"]
    },
    "evaluate_writing_clarity": {
        "fn": evaluate_writing_clarity,
        "args": ["agent", "input_arg"]
    },
    "check_fact_substantiation": {
        "fn": check_fact_substantiation,
        "args": ["agent", "input_arg"]
    },
    "check_for_unsupported_assumptions": {
        "fn": check_for_unsupported_assumptions,
        "args": ["agent", "input_arg"]
    },

    # Team Tools
    "evaluate_collaboration_approach": {
        "fn": evaluate_collaboration_approach,
        "args": ["agent", "input_arg"]
    },
    "check_team_experience_alignment": {
        "fn": check_team_experience_alignment,
        "args": ["agent", "input_arg"]
    },
    "detect_bait_and_switch_risk": {
        "fn": detect_bait_and_switch_risk,
        "args": ["agent", "input_arg"]
    },
    "check_local_resource_presence": {
        "fn": check_local_resource_presence,
        "args": ["agent", "input_arg"]
    },

    # Vendor Experience Tools
    "check_vendor_experience_relevance": {
        "fn": check_vendor_experience_relevance,
        "args": ["agent", "input_arg"]
    },
    "check_vendor_experience_evidence": {
        "fn": check_vendor_experience_evidence,
        "args": ["agent", "input_arg"]
    },

    # Implementation Plan Tools
    "check_implementation_milestones": {
        "fn": check_implementation_milestones,
        "args": ["agent", "input_arg"]
    },
    "check_resource_plan_realism": {
        "fn": check_resource_plan_realism,
        "args": ["agent", "input_arg"]
    },
    "check_assumption_reasonableness": {
        "fn": check_assumption_reasonableness,
        "args": ["agent", "input_arg"]
    },
    "check_timeline_feasibility": {
        "fn": check_timeline_feasibility,
        "args": ["agent", "input_arg"]
    },
    "check_contingency_plans": {
        "fn": check_contingency_plans,
        "args": ["agent", "input_arg"]
    },

    # Methodology Tools
    "check_discovery_approach": {
        "fn": check_discovery_approach,
        "args": ["agent", "input_arg"]
    },
    "check_requirements_approach": {
        "fn": check_requirements_approach,
        "args": ["agent", "input_arg"]
    },
    "check_design_approach": {
        "fn": check_design_approach,
        "args": ["agent", "input_arg"]
    },
    "check_build_approach": {
        "fn": check_build_approach,
        "args": ["agent", "input_arg"]
    },
    "check_test_approach": {
        "fn": check_test_approach,
        "args": ["agent", "input_arg"]
    },
    "check_deployment_approach": {
        "fn": check_deployment_approach,
        "args": ["agent", "input_arg"]
    },
    "check_operate_approach": {
        "fn": check_operate_approach,
        "args": ["agent", "input_arg"]
    },
    "check_agile_compatibility": {
        "fn": check_agile_compatibility,
        "args": ["agent", "input_arg"]
    },
    "check_accelerators_and_tools": {
        "fn": check_accelerators_and_tools,
        "args": ["agent", "input_arg"]
    },

    # Cost Tools
    "check_value_for_money": {
        "fn": check_value_for_money,
        "args": ["agent", "input_arg"]
    },
    "check_cost_benchmark": {
        "fn": check_cost_benchmark,
        "args": ["agent", "input_arg"]
    },
    "generate_cost_forecast": {
        "fn": generate_cost_forecast,
        "args": ["agent", "input_arg"]
    },

    # Risk Tools
    "check_data_privacy_and_security_measures": {
        "fn": check_data_privacy_and_security_measures,
        "args": ["agent", "input_arg"]
    },
    "check_risk_register_or_mitigation_plan": {
        "fn": check_risk_register_or_mitigation_plan,
        "args": ["agent", "input_arg"]
    },
    "check_compliance_certifications": {
        "fn": check_compliance_certifications,
        "args": ["agent", "input_arg"]
    },

    # Solution Fit Tools
    "evaluate_product_fit": {
        "fn": evaluate_product_fit,
        "args": ["agent", "input_arg"]
    },
    "evaluate_nfr_support": {
        "fn": evaluate_nfr_support,
        "args": ["agent", "input_arg"]
    },
    "evaluate_modularity_and_scalability": {
        "fn": evaluate_modularity_and_scalability,
        "args": ["agent", "input_arg"]
    },
    "check_product_roadmap": {
        "fn": check_product_roadmap,
        "args": ["agent", "input_arg"]
    },
    "evaluate_demos_and_proofs": {
        "fn": evaluate_demos_and_proofs,
        "args": ["agent", "input_arg"]
    }
}
