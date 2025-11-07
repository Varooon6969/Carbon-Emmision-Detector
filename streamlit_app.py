import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ========== Helper Functions ==========

def calculate_emissions(electricity, lpg, transport_km, fuel_type, nonveg_meals, waste, water):
    transport_factor = {"Petrol": 0.2, "Diesel": 0.27, "CNG": 0.15, "Electric": 0.05}
    diet_factor = {"Vegetarian": 1.5, "Mixed": 2.5, "Non-Vegetarian": 3.5}

    emissions = {
        "Electricity": electricity * 0.82,
        "LPG": lpg * 2.9,
        "Transport": transport_km * 30 * transport_factor.get(fuel_type, 0.2),
        "Diet": nonveg_meals * diet_factor.get("Mixed", 2.5) * 4,
        "Waste": waste * 1.5 * 4,
        "Water": (water / 1000) * 0.35,
    }
    return emissions


def get_suggestion(category):
    suggestions = {
        "Electricity": "💡 Switch to LED bulbs and energy-efficient appliances.",
        "LPG": "🔥 Cook with lids on and use induction cooktops.",
        "Transport": "🚗 Carpool or use public transport when possible.",
        "Diet": "🥦 Reduce red-meat and include more plant-based meals.",
        "Waste": "♻️ Recycle and compost organic waste.",
        "Water": "💧 Fix leaks and reuse water where possible.",
    }
    return suggestions.get(category, "✅ Keep up your sustainable habits!")


# ========== Streamlit UI ==========

st.set_page_config(page_title="CarbonAI v2 — Smart Sustainability Advisor", page_icon="🌎")
st.title("🌱 CarbonAI v2 — Smart Sustainability Advisor")

st.write("Estimate your household’s monthly carbon footprint and get AI-based suggestions.")

# ---- Input Fields ----
electricity = st.number_input("Electricity Usage (kWh/month)", 0.0)
lpg = st.number_input("LPG Consumption (kg/month)", 0.0)
transport_km = st.number_input("Average Daily Transport Distance (km)", 0.0)
fuel_type = st.selectbox("Transport Fuel Type", ["Petrol", "Diesel", "CNG", "Electric"])
nonveg_meals = st.number_input("Non-veg Meals per Week", 0.0)
waste = st.number_input("Household Waste (kg/week)", 0.0)
water = st.number_input("Water Consumption (liters/month)", 0.0)

if st.button("Predict Carbon Footprint"):
    emissions = calculate_emissions(
        electricity, lpg, transport_km, fuel_type, nonveg_meals, waste, water
    )
    total_emission = sum(emissions.values())
    st.success(f"🌍 Estimated Total: **{total_emission:.2f} kg CO₂/month**")

    # ---- Charts ----
    emission_df = pd.DataFrame(list(emissions.items()), columns=["Category", "Emission"])
    st.bar_chart(emission_df.set_index("Category"))

    st.subheader("📊 Emission Contribution by Category")
    fig, ax = plt.subplots()
    ax.pie(
        emission_df["Emission"],
        labels=emission_df["Category"],
        autopct="%1.1f%%",
        startangle=90,
    )
    ax.axis("equal")
    st.pyplot(fig)

    # ---- Top Categories ----
    sorted_emissions = sorted(emissions.items(), key=lambda x: x[1], reverse=True)
    top_cat, top_val = sorted_emissions[0]
    second_cat, second_val = sorted_emissions[1]

    st.markdown("---")
    st.write(f"🔸 **Top Contributor:** {top_cat} — {top_val:.2f} kg CO₂/month")
    st.write(f"🔸 **Second Contributor:** {second_cat} — {second_val:.2f} kg CO₂/month")

    # ---- Suggestions ----
    st.info(f"🌱 To reduce {top_cat}: {get_suggestion(top_cat)}")
    st.info(f"🌿 To improve {second_cat}: {get_suggestion(second_cat)}")

    # ---- Reduction Estimate ----
    reduction_estimates = {
        "Electricity": 0.25,
        "LPG": 0.15,
        "Transport": 0.30,
        "Diet": 0.20,
        "Waste": 0.25,
        "Water": 0.10,
    }
    reduction_1 = top_val * reduction_estimates.get(top_cat, 0.2)
    reduction_2 = second_val * reduction_estimates.get(second_cat, 0.2)
    total_reduction = reduction_1 + reduction_2
    new_total = total_emission - total_reduction
    reduction_percent = (total_reduction / total_emission) * 100

    st.markdown("### 🌏 Estimated Carbon Reduction Potential")
    st.success(
        f"If you follow suggestions for **{top_cat}** and **{second_cat}**, "
        f"you could reduce emissions by **{reduction_percent:.1f}%**, "
        f"bringing your footprint down to **{new_total:.1f} kg CO₂/month.**"
    )
