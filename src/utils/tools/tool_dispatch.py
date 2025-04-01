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
    "check_guideline_dynamic": check_guideline_dynamic,
    "detect_boilerplate_or_marketing_fluff": detect_boilerplate_or_marketing_fluff,
    "evaluate_writing_clarity": evaluate_writing_clarity,
    "check_fact_substantiation": check_fact_substantiation,
    "check_for_unsupported_assumptions": check_for_unsupported_assumptions,

    # Team Tools
    "evaluate_collaboration_approach": evaluate_collaboration_approach,
    "check_team_experience_alignment": check_team_experience_alignment,
    "detect_bait_and_switch_risk": detect_bait_and_switch_risk,
    "check_local_resource_presence": check_local_resource_presence,

    # Vendor Experience Tools
    "check_vendor_experience_relevance": check_vendor_experience_relevance,
    "check_vendor_experience_evidence": check_vendor_experience_evidence,

    # Implementation Plan Tools
    "check_implementation_milestones": check_implementation_milestones,
    "check_resource_plan_realism": check_resource_plan_realism,
    "check_assumption_reasonableness": check_assumption_reasonableness,
    "check_timeline_feasibility": check_timeline_feasibility,
    "check_contingency_plans": check_contingency_plans,

    # Methodology Tools
    "check_discovery_approach": check_discovery_approach,
    "check_requirements_approach": check_requirements_approach,
    "check_design_approach": check_design_approach,
    "check_build_approach": check_build_approach,
    "check_test_approach": check_test_approach,
    "check_deployment_approach": check_deployment_approach,
    "check_operate_approach": check_operate_approach,
    "check_agile_compatibility": check_agile_compatibility,
    "check_accelerators_and_tools": check_accelerators_and_tools,

    # Cost Tools
    "check_value_for_money": check_value_for_money,
    "check_cost_benchmark": check_cost_benchmark,
    "generate_cost_forecast": generate_cost_forecast,

    # Risk Tools
    "check_data_privacy_and_security_measures": check_data_privacy_and_security_measures,
    "check_risk_register_or_mitigation_plan": check_risk_register_or_mitigation_plan,
    "check_compliance_certifications": check_compliance_certifications,

    # Solution Fit Tools
    "evaluate_product_fit": evaluate_product_fit,
    "evaluate_nfr_support": evaluate_nfr_support,
    "evaluate_modularity_and_scalability": evaluate_modularity_and_scalability,
    "check_product_roadmap": check_product_roadmap,
    "evaluate_demos_and_proofs": evaluate_demos_and_proofs
}
