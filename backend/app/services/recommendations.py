from datetime import date
from typing import Dict, Any

def get_cycle_phase(start_date: date, current_date: date, avg_cycle_length: int = 28) -> str:
    """
    Determines the current menstrual cycle phase based on cycle start date and average cycle length.
    """
    delta_days = (current_date - start_date).days
    
    # Wrap index within cycle length just in case the cycle is delayed
    day_in_cycle = (delta_days % avg_cycle_length) + 1
    
    if 1 <= day_in_cycle <= 5:
        return "Menstrual"
    elif 6 <= day_in_cycle <= 13:
        return "Follicular"
    elif 14 <= day_in_cycle <= 16:
        return "Ovulatory"
    else:
        return "Luteal"

def get_phase_recommendations(phase: str) -> Dict[str, Any]:
    """
    Returns dietary, exercise, and symptom-mitigation advice customized for the specific phase.
    """
    recommendations = {
        "Menstrual": {
            "phase_name": "Menstrual Phase (Days 1-5)",
            "hormones": "Estrogen and progesterone are at their lowest levels.",
            "diet": [
                "Prioritize iron-rich foods like leafy greens, lentils, and lean red meats.",
                "Incorporate healthy fats (avocados, wild-caught fish) to support hormone production.",
                "Sip anti-inflammatory teas like ginger or chamomile to ease cramping."
            ],
            "exercise": [
                "Focus on low-impact movement and active recovery.",
                "Gentle walking, light stretching, or yin yoga are ideal.",
                "Listen to your body and prioritize rest if feeling highly fatigued."
            ],
            "pcos_focus": "Insulin sensitivity can be slightly lower. Avoid sudden sugar spikes by pairing any carbohydrates with protein and fiber."
        },
        "Follicular": {
            "phase_name": "Follicular Phase (Days 6-13)",
            "hormones": "Estrogen and follicle-stimulating hormone (FSH) are steadily rising.",
            "diet": [
                "Enjoy light, fresh foods and fermented options (kimchi, sauerkraut, kefir) for gut health.",
                "Include healthy seeds (pumpkin and flax seeds) to encourage balanced estrogen levels.",
                "Build meals with lean proteins, broccoli, cruciferous vegetables, and sprouts."
            ],
            "exercise": [
                "Take advantage of rising energy levels with regular strength training.",
                "Moderate cardio, power yoga, and bodyweight exercises are highly effective.",
                "This is an excellent phase to build new muscle tissue."
            ],
            "pcos_focus": "Increasing estrogen aids insulin sensitivity. It is a prime window for building muscle and managing body composition."
        },
        "Ovulatory": {
            "phase_name": "Ovulatory Phase (Days 14-16)",
            "hormones": "Estrogen levels peak, triggering a surge in Luteinizing Hormone (LH) which releases the egg.",
            "diet": [
                "Incorporate plenty of fiber and raw vegetables (carrots, leafy greens) to help clear excess estrogen.",
                "Hydrate thoroughly with water, coconut water, or infused herbal waters.",
                "Enjoy antioxidant-rich fruits like berries, citrus, and dark leafy greens."
            ],
            "exercise": [
                "High-intensity interval training (HIIT), spinning, or heavy strength sessions match peak energy levels.",
                "Engage in challenging workouts that match your high stamina."
            ],
            "pcos_focus": "Supports clearing of metabolized estrogen. Excessive estrogen dominance is common in PCOS; high fiber intake is essential here."
        },
        "Luteal": {
            "phase_name": "Luteal Phase (Days 17-28+)",
            "hormones": "Progesterone is the dominant hormone, peaking and then falling if fertilization doesn't occur.",
            "diet": [
                "Eat complex carbohydrates (sweet potatoes, pumpkin, quinoa) to help boost serotonin and curb sweet cravings.",
                "Add magnesium-rich foods (dark chocolate >70%, spinach, pumpkin seeds) to calm the nervous system.",
                "Start seed syncing with sesame and sunflower seeds."
            ],
            "exercise": [
                "Pivot towards moderate-intensity exercises like pilates, medium strength training, and standard cardio.",
                "In the latter half of this phase, reduce intensity to support progesterone levels and prevent excess cortisol production."
            ],
            "pcos_focus": "Insulin resistance can intensify during the luteal phase, leading to increased cravings. Focus on stable, high-fiber, high-protein meals."
        }
    }
    
    return recommendations.get(phase, recommendations["Menstrual"])
