def dispatch_tool_action_archive(agent, action, report_sections=None):
    """
    Purpose:
        Dispatches a tool action based on the provided action string and executes the corresponding function.

    Parameters:
        agent (object): The agent object containing context such as section text, section name, and memory.
        action (str): The action string specifying the tool action to be executed.

    Workflow:
        1. Logs the tool action being executed.
        2. Matches the action string against predefined patterns using regular expressions.
        3. Executes the corresponding function based on the matched action.
        4. Handles specific cases such as academic support, citation checks, and section upgrades.
        5. Returns the result of the executed function or an appropriate message if the action is unrecognized.

    Returns:
        str: The result of the executed tool action or an error message if an exception occurs.
    """
    print(f"🛠️ Tool action: {action}")

    # Check if the action matches the format of a known tool
    known_tool_names = list(tool_catalog.keys())
    recognized = False

    for tool in known_tool_names:
        if action.startswith(tool):
            recognized = True
            break

    if not recognized:
        return f"⚠️ Unrecognized action: {action}. Please check the action format or choose a valid tool."

    try:
        # general tools
        if action.startswith("check_guideline"):
            match = re.match(r'check_guideline\["(.+?)"\]', action)
            if match:
                return check_guideline_dynamic(match.group(1),agent)
        elif action.startswith("detect_boilerplate_or_marketing_fluff"):
            match = re.match(r'detect_boilerplate_or_marketing_fluff\["(.+?)"\]', action)
            if match:
                text = match.group(1)
                try:
                    return detect_boilerplate_or_marketing_fluff(agent)
                except Exception as e:
                    return f"⚠️ Tool execution error: {e}"
            else:
                return "⚠️ Could not parse detect_boilerplate_or_marketing_fluff action."
        elif action.startswith("evaluate_writing_clarity"):
            match = re.match(r'evaluate_writing_clarity\["(.+?)"\]', action)
            if match:
                text = match.group(1)
                try:
                    return evaluate_writing_clarity(agent)
                except Exception as e:
                    return f"⚠️ Tool execution error: {e}"
            else:
                return "⚠️ Could not parse evaluate_writing_clarity action."
        elif action.startswith("check_fact_substantiation"):
            match = re.match(r'check_fact_substantiation\["(.+?)"\]', action)
            if match:
                return check_fact_substantiation(agent)        
        elif action.startswith("check_for_unsupported_assumptions"):
            match = re.match(r'check_for_unsupported_assumptions\["(.+?)"\]', action)
            if match:
                return check_for_unsupported_assumptions(agent)
            
        # RFP: team tools
        elif action.startswith("evaluate_collaboration_approach"):
            match = re.match(r'evaluate_collaboration_approach\["(.+?)"\]', action)
            if match:
                return evaluate_collaboration_approach(agent)
        elif action.startswith("check_team_experience_alignment"):
            match = re.match(r'check_team_experience_alignment\["(.+?)"\]', action)
            if match:
                return check_team_experience_alignment(agent)
            else:
                return "⚠️ Could not parse check_team_experience_alignment action."
        elif action.startswith("detect_bait_and_switch_risk"):
            match = re.match(r'detect_bait_and_switch_risk\["(.+?)"\]', action)
            if match:
                return detect_bait_and_switch_risk(agent)
            else:
                return "⚠️ Could not parse detect_bait_and_switch_risk action."
        elif action.startswith("check_local_resource_presence"):
            match = re.match(r'check_local_resource_presence\["(.+?)"\]', action)
            if match:
                return check_local_resource_presence(agent)
            else:
                return "⚠️ Could not parse check_local_resource_presence action."
            
        # RFP: experience tools
        elif action.startswith("check_vendor_experience_relevance"):
            match = re.match(r'check_vendor_experience_relevance\["(.+?)"\]', action)
            if match:
                return check_vendor_experience_relevance(agent)
        elif action.startswith("check_vendor_experience_evidence"):
            match = re.match(r'check_vendor_experience_evidence\["(.+?)"\]', action)
            if match:
                return check_vendor_experience_evidence(agent)
            
        # RFP: plan tools
        elif action.startswith("check_timeline_feasibility"):
            match = re.match(r'check_timeline_feasibility\["(.+?)"\]', action)
            if match:
                return check_timeline_feasibility(agent)
        elif action.startswith("check_contingency_plans"):
            match = re.match(r'check_contingency_plans\["(.+?)"\]', action)
            if match:
                return check_contingency_plans(agent)
        elif action.startswith("check_implementation_milestones"):
            match = re.match(r'check_implementation_milestones\["(.+?)"\]', action)
            if match:
                return check_implementation_milestones(agent)
        elif action.startswith("check_resource_plan_realism"):
            match = re.match(r'check_resource_plan_realism\["(.+?)"\]', action)
            if match:
                return check_resource_plan_realism(agent)
        elif action.startswith("check_assumption_reasonableness"):
            match = re.match(r'check_assumption_reasonableness\["(.+?)"\]', action)
            if match:
                return check_assumption_reasonableness(agent)
        
        # RFP: method tools
        elif action.startswith("check_discovery_approach"):
            match = re.match(r'check_discovery_approach\["(.+?)"\]', action)
            if match:
                return check_discovery_approach(agent)
        elif action.startswith("check_requirements_approach"):
            match = re.match(r'check_requirements_approach\["(.+?)"\]', action)
            if match:
                return check_requirements_approach(agent)
        elif action.startswith("check_design_approach"):
            match = re.match(r'check_design_approach\["(.+?)"\]', action)
            if match:
                return check_design_approach(agent)
        elif action.startswith("check_build_approach"):
            match = re.match(r'check_build_approach\["(.+?)"\]', action)
            if match:
                return check_build_approach(agent)
        elif action.startswith("check_test_approach"):
            match = re.match(r'check_test_approach\["(.+?)"\]', action)
            if match:
                return check_test_approach(agent)
        elif action.startswith("check_deployment_approach"):
            match = re.match(r'check_deployment_approach\["(.+?)"\]', action)
            if match:
                return check_deployment_approach(agent)
        elif action.startswith("check_operate_approach"):
            match = re.match(r'check_operate_approach\["(.+?)"\]', action)
            if match:
                return check_operate_approach(agent)
        elif action.startswith("check_agile_compatibility"):
            match = re.match(r'check_agile_compatibility\["(.+?)"\]', action)
            if match:
                return check_agile_compatibility(agent)
        elif action.startswith("check_accelerators_and_tools"):
            match = re.match(r'check_accelerators_and_tools\["(.+?)"\]', action)
            if match:
                return check_accelerators_and_tools(agent)
        
        # RFP: cost/value tools
        elif action.startswith("check_value_for_money"):
            match = re.match(r'check_value_for_money\["(.+?)"\]', action)
            if match:
                return check_value_for_money(agent)
        elif action.startswith("check_cost_benchmark"):
            match = re.match(r'check_cost_benchmark\["(.+?)"\]', action)
            if match:
                return check_cost_benchmark(agent)
        elif action.startswith("generate_cost_forecast"):
            match = re.match(r'generate_cost_forecast\["(.+?)"\]', action)
            if match:
                return generate_cost_forecast(agent)

        # RFP: risk tools
        elif action.startswith("check_data_privacy_and_security_measures"):
            match = re.match(r'check_data_privacy_and_security_measures\["(.+?)"\]', action)
            if match:
                return check_data_privacy_and_security_measures(agent)
        elif action.startswith("check_risk_register_or_mitigation_plan"):
            match = re.match(r'check_risk_register_or_mitigation_plan\["(.+?)"\]', action)
            if match:
                return check_risk_register_or_mitigation_plan(agent)
        elif action.startswith("check_compliance_certifications"):
            match = re.match(r'check_compliance_certifications\["(.+?)"\]', action)
            if match:
                return check_compliance_certifications(agent)

        # RFP: fit tools
        elif action.startswith("evaluate_product_fit"):
            match = re.match(r'evaluate_product_fit\["(.+?)"\]', action)
            if match:
                return evaluate_product_fit(agent)

        elif action.startswith("evaluate_nfr_support"):
            match = re.match(r'evaluate_nfr_support\["(.+?)"\]', action)
            if match:
                return evaluate_nfr_support(agent)

        elif action.startswith("evaluate_modularity_and_scalability"):
            match = re.match(r'evaluate_modularity_and_scalability\["(.+?)"\]', action)
            if match:
                return evaluate_modularity_and_scalability(agent)

        elif action.startswith("check_product_roadmap"):
            match = re.match(r'check_product_roadmap\["(.+?)"\]', action)
            if match:
                return check_product_roadmap(agent)

        elif action.startswith("evaluate_demos_and_proofs"):
            match = re.match(r'evaluate_demos_and_proofs\["(.+?)"\]', action)
            if match:
                return evaluate_demos_and_proofs(agent)


        elif action.startswith("keyword_match_in_section"):
            match = re.match(r'keyword_match_in_section\["(.+?)"\]', action)
            if match:
                return keyword_match_in_section(match.group(1), agent)
        elif action.startswith("check_timeline_feasibility"):
            match = re.match(r'check_timeline_feasibility\["(.+?)"\]', action)
            if match:
                return check_timeline_feasibility(agent)
        elif action.startswith("search_report"):
            match = re.match(r'search_report\["(.+?)"\]', action)
            if match:
                return search_report(match.group(1), report_sections)
        elif action.startswith("search_web"):
            match = re.match(r'search_web\["(.+?)"\]', action)
            if match:
                return search_web(match.group(1))
        elif action == "generate_client_questions":
            return generate_client_questions(agent)
        elif action.startswith("check_summary_support"):
            match = re.match(r'check_summary_support\["(.+?)"\]', action)
            if match:
                return check_summary_support(match.group(1), report_sections)
        elif action == "evaluate_smart_goals":
            return evaluate_smart_goals(agent)
        elif action.startswith("check_recommendation_alignment"):
            match = re.match(r'check_recommendation_alignment\["(.+?)"\]', action)
            if match:
                if report_sections is None:
                    return "⚠️ Cannot check alignment — full report context not available."
                else:
                    goals = report_sections.get("Goals & Objectives", "")
                    return check_recommendation_alignment(match.group(1), goals)
        elif action == "ask_question":
            return "Good question to ask the client for clarification."
        elif action == "flag_risk":
            return "This is a legitimate risk that should be addressed."
        elif action == "recommend_fix":
            return "The recommendation improves the section's clarity and compliance."
        elif action == "summarize":
            return "Review complete."
        elif action == "tool_help":
            return format_tool_catalog_for_prompt(tool_catalog)
        elif action.startswith("suggest_tool_for"):
            match = re.match(r'suggest_tool_for\["(.+?)"\]', action)
            if match:
                matches = pick_tool_by_intent_fuzzy(match.group(1), tool_catalog)
                if matches:
                    return "Best match based on your goal:\n" + "\n".join([f"{tool} (match: {score})" for tool, score in matches])
                else:
                    return "⚠️ No matching tool found. Showing available tools:\n" + format_tool_catalog_for_prompt(tool_catalog)
        elif action == "final_summary":
            return generate_final_summary(agent)
        elif action.startswith("search_wikipedia"):
            match = re.match(r'search_wikipedia\["(.+?)"\]', action)
            if match:
                query = match.group(1)
                return search_wikipedia(query)
            else:
                return "⚠️ Could not parse search_wikipedia action."
        elif action == "analyze_tone_textblob":
            return analyze_tone_textblob(agent)
        elif action.startswith("search_serpapi"):
            match = re.match(r'search_serpapi\["(.+?)"\]', action)
            if match:
                query = match.group(1)
                return search_serpapi(query, agent)
            else:
                return "⚠️ Could not parse search_serpapi action."
        elif action == "extract_named_entities":
            return extract_named_entities(agent)
        elif action.startswith("analyze_math_question"):
            match = re.match(r'analyze_math_question\["(.+?)"\]', action)
            if match:
                expr = match.group(1)
                return analyze_math_question(expr)
            else:
                return "⚠️ Could not parse analyze_math_question action."
        elif action.startswith("search_arxiv"):
            match = re.match(r'search_arxiv\["(.+?)"\]', action)
            if match:
                query = match.group(1)
                return search_arxiv(query, agent)
            else:
                # Fallback for poorly formatted call
                query = action.replace("search_arxiv", "").strip(" -:\"")
                return search_arxiv(query, agent)
        elif action == "auto_check_for_academic_support":
            needs_citation, reason = should_search_arxiv(agent)
            if needs_citation:
                # Automatically create and run an arxiv search
                followup_action = f'search_arxiv["{agent.section_name}"]'
                followup_obs = dispatch_tool_action(agent, followup_action, report_sections)
                # Log follow-up to memory
                agent.memory.setdefault("academic_support", {})[agent.section_name] = {
                    "reason": reason,
                    "action": followup_action,
                    "observation": followup_obs
                }
                return f"✅ Academic support was added.\nReason: {reason}\n\n{followup_obs}"
            else:
                return f"🟢 No academic support needed.\nReason: {reason}"
        elif action.startswith("should_cite"):
            match = re.match(r'should_cite\["(.+?)"\]', action)
            if match:
                statement = match.group(1)
                needs, reason = should_cite(statement)
                if needs:
                    # Run research-based rewrite
                    improved = auto_fill_gaps_with_research(statement)
                    observation = (
                        f"✅ Citation recommended. Reason: {reason}\n\n"
                        f"📚 Improved statement with research:\n{improved}"
                    )
                    agent.memory.setdefault("enhanced_statements", {})[statement] = improved
                    return observation
                else:
                    observation = f"🟢 No citation needed. Reason: {reason}"
                    return observation
            else:
                return "⚠️ Could not parse should_cite action."
        elif action == "auto_fill_gaps_with_research":
            return auto_fill_gaps_with_research(agent)
        elif action == "upgrade_section_with_research":
            improved, log, footnotes = upgrade_section_with_research(agent)
            observation = "🧠 Section upgraded with research. Rewrites:\n"
            for change in log:
                observation += f"- 🔹 '{change['original']}'\n  🧠 → {change['improved']}\n  📚 Reason: {change['reason']}\n\n"

            # Store in memory for final report
            agent.memory.setdefault("section_upgrades", {})[agent.section_name] = {
                "original": agent.section_text,
                "improved": improved,
                "log": log,
                "footnotes": footnotes
            }

            return observation
        else:
            return f"⚠️ Unrecognized action: {action}. Please check the action format."
    except Exception as e:
        return f"⚠️ Tool execution error: {str(e)}"
