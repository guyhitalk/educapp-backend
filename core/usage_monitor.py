# core/usage_monitor.py
"""
API Usage Monitoring for EducApp
Tracks token usage and estimates costs for Anthropic Claude API
"""

import os
from datetime import datetime
from core.database_supabase import SupabaseDatabase

# Initialize database
db = SupabaseDatabase()

# Claude 3 Opus Pricing (as of Nov 2024)
INPUT_COST_PER_1M_TOKENS = 15.00   # $15 per 1M input tokens
OUTPUT_COST_PER_1M_TOKENS = 75.00  # $75 per 1M output tokens

# Claude 3.5 Sonnet Pricing (for future upgrade)
SONNET_INPUT_COST_PER_1M = 3.00
SONNET_OUTPUT_COST_PER_1M = 15.00


def estimate_cost(input_tokens, output_tokens, model='claude-3-opus'):
    """
    Estimate cost for an API call
    
    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: Model name ('claude-3-opus' or 'claude-3-5-sonnet')
    
    Returns:
        Estimated cost in USD
    """
    if model == 'claude-3-5-sonnet':
        input_cost_per_1m = SONNET_INPUT_COST_PER_1M
        output_cost_per_1m = SONNET_OUTPUT_COST_PER_1M
    else:  # Default to Opus
        input_cost_per_1m = INPUT_COST_PER_1M_TOKENS
        output_cost_per_1m = OUTPUT_COST_PER_1M_TOKENS
    
    input_cost = (input_tokens / 1_000_000) * input_cost_per_1m
    output_cost = (output_tokens / 1_000_000) * output_cost_per_1m
    
    total_cost = input_cost + output_cost
    return round(total_cost, 6)  # Round to 6 decimal places


def format_cost(cost_usd):
    """Format cost in both USD and BRL"""
    cost_brl = cost_usd * 5.0  # Approximate conversion rate
    return f"${cost_usd:.4f} (R${cost_brl:.2f})"


def track_api_call(user_email, input_tokens, output_tokens, model='claude-3-opus'):
    """
    Track an API call and log to database
    
    Args:
        user_email: User's email address
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: Model name
    
    Returns:
        Estimated cost in USD
    """
    # Note: API call logging not yet implemented in Supabase
    # This is a placeholder for future implementation
    estimated_cost = estimate_cost(input_tokens, output_tokens, model)
    
    # TODO: Add API call logging to Supabase database
    # db.log_api_call(user_email, input_tokens, output_tokens, estimated_cost, model)
    
    return estimated_cost


def get_user_monthly_stats(user_email):
    """
    Get user's usage statistics for current month
    
    Returns:
        Dictionary with usage stats
    """
    # Note: Detailed usage tracking not yet implemented
    # This is a placeholder for future implementation
    
    # TODO: Add monthly cost tracking to Supabase
    # total_cost = db.get_monthly_cost(user_email)
    # total_questions = db.get_monthly_usage(user_email)
    
    user = db.get_user_by_email(user_email)
    total_questions = user.get('questions_asked', 0) if user else 0
    
    # Rough estimate based on questions asked
    total_cost = total_questions * 0.05  # Approximate $0.05 per question
    avg_cost_per_question = total_cost / total_questions if total_questions > 0 else 0
    
    return {
        'total_cost': total_cost,
        'total_questions': total_questions,
        'avg_cost_per_question': avg_cost_per_question
    }


def check_cost_alert(user_email, threshold_usd=5.00):
    """
    Check if user has exceeded cost threshold
    
    Args:
        user_email: User's email
        threshold_usd: Alert threshold in USD
    
    Returns:
        Boolean indicating if threshold exceeded
    """
    stats = get_user_monthly_stats(user_email)
    return stats['total_cost'] > threshold_usd


def estimate_monthly_burn_rate():
    """
    Estimate total monthly burn rate across all users
    
    Returns:
        Dictionary with burn rate statistics
    """
    # Note: Detailed API cost tracking not yet implemented
    # This is a placeholder for future implementation
    
    # TODO: Add comprehensive API cost tracking to Supabase
    user_stats = db.get_user_stats()
    
    free_users = user_stats.get('free_users', 0)
    paid_users = user_stats.get('paid_users', 0)
    total_questions = user_stats.get('total_questions', 0)
    
    # Rough estimate
    total_cost = total_questions * 0.05  # ~$0.05 per question
    avg_cost_per_call = 0.05
    
    # Calculate revenue
    monthly_revenue = paid_users * 15  # $15 per paid user
    
    # Calculate profit/loss
    profit = monthly_revenue - total_cost
    
    return {
        'total_cost': total_cost,
        'monthly_revenue': monthly_revenue,
        'profit_loss': profit,
        'free_users': free_users,
        'paid_users': paid_users,
        'total_calls': total_questions,
        'avg_cost_per_call': avg_cost_per_call
    }


if __name__ == "__main__":
    # Test cost estimation
    print("🧪 Testing Usage Monitor\n")
    
    # Example: Typical EducApp conversation
    test_input_tokens = 2000   # ~1500 words context + question
    test_output_tokens = 500   # ~375 word response
    
    cost_opus = estimate_cost(test_input_tokens, test_output_tokens, 'claude-3-opus')
    cost_sonnet = estimate_cost(test_input_tokens, test_output_tokens, 'claude-3-5-sonnet')
    
    print(f"Claude 3 Opus:")
    print(f"  Input: {test_input_tokens} tokens")
    print(f"  Output: {test_output_tokens} tokens")
    print(f"  Cost: {format_cost(cost_opus)}\n")
    
    print(f"Claude 3.5 Sonnet (future):")
    print(f"  Input: {test_input_tokens} tokens")
    print(f"  Output: {test_output_tokens} tokens")
    print(f"  Cost: {format_cost(cost_sonnet)}\n")
    
    print(f"💰 Savings with Sonnet: {format_cost(cost_opus - cost_sonnet)}")
    print(f"📊 Sonnet is {((cost_opus - cost_sonnet) / cost_opus * 100):.1f}% cheaper")