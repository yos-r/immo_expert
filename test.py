from experta import *

# prix terrain mètre carré 
NEIGHBORHOOD_PRICES = {
    "centre urbain nord": 3500,
    "ariana": 2200,
    "mutuelleville": 2700,
    "alain savary": 2900,
    "menzah 1": 2450,
    "menzah 4": 2500,
}

class Property(Fact):
    """Fact class representing property details."""
    pass

class PropertyValuationEngine(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.base_value = 0
        self.adjustments = []

    

    @Rule(AND(Property(condition='excellent'), Property(standing='high')))
    def condition_excellent_high(self):
        self.adjustments.append(("Excellent Condition / High Standing", 0.25))
      
    @Rule(AND(Property(condition='good'), Property(standing='medium')))
    def condition_good_medium(self):
        self.adjustments.append(("Good Condition / Medium Standing", 0.15))
    
    @Rule(AND(Property(condition='poor'), Property(standing='medium')))
    def condition_poor_medium(self):
        self.adjustments.append(("Poor Condition / Medium Standing", -0.1))

    
    @Rule(AND(Property(market_demand=MATCH.market_demand), TEST(lambda market_demand: market_demand > 80)))
    def very_high_market_demand(self, market_demand):
        self.adjustments.append(("Very High Market Demand", 0.25))
    @Rule(AND(
    Property(market_demand=MATCH.market_demand),
    TEST(lambda market_demand: market_demand >= 50),
    TEST(lambda market_demand: market_demand <= 80)
    ))
    def high_market_demand(self, market_demand):
        self.adjustments.append(("High Market Demand", 0.20))


    @Rule(AND(Property(market_demand=MATCH.market_demand), TEST(lambda market_demand: market_demand >= 20),
    TEST(lambda market_demand: market_demand <= 50)))
    def medium_market_demand(self, market_demand):
        self.adjustments.append(("Medium Market Demand", 0.15))

    @Rule(AND(Property(market_demand=MATCH.market_demand), TEST(lambda market_demand: 10 <= market_demand < 20)))
    def low_market_demand(self, market_demand):
        self.adjustments.append(("Low Market Demand", -0.10))

    @Rule(AND(Property(market_demand=MATCH.market_demand), TEST(lambda market_demand: market_demand < 10)))
    def very_low_market_demand(self, market_demand):
        self.adjustments.append(("Very Low Market Demand", -0.15))

    @Rule(Property(amenities=MATCH.amenities))
    def amenities_rules(self, amenities):
        amenity_mappings = {
            "air_conditioning": ("Air Conditioning", 0.05),
            "central_heating": ("Central Heating", 0.05),
            "pool": ("Pool", 0.15),
            "optical_fiber": ("Optical Fiber", 0.05),
            "alarm": ("Alarm", 0.02),
            "camera": ("Surveilance Camera", 0.05),
            "garden": ("Garden", 0.15)
        }
        
        for amenity, (desc, value) in amenity_mappings.items():
            if amenity in amenities:
                self.adjustments.append((desc, value))

    @Rule(Property(rooms=MATCH.rooms))
    def extra_rooms_bonus(self, rooms):
        if rooms > 3:
            self.adjustments.append(("Extra Rooms", 0.2))
    @Rule(Property(bathrooms=MATCH.bathrooms))
    def no_bathroom_penalty(self, bathrooms):
        if bathrooms == 0:
            self.adjustments.append(("No Bathrooms", -0.1))

    @Rule(Property(bathrooms=MATCH.bathrooms))
    def extra_bathroom_bonus(self, bathrooms):
        if bathrooms > 2:
            self.adjustments.append(("Extra Bathrooms", 0.1))

    @Rule(Property(parkings=MATCH.parkings))
    def parking_rules(self, parkings):
        if parkings == 0:
            self.adjustments.append(("No Parking", -0.2))
        elif parkings >= 2:
            self.adjustments.append(("Multiple Parking Spaces", 0.15))

    @Rule(
        AND(
            Property(size=MATCH.size, neighborhood=MATCH.neighborhood),
            Property(pty_type='villa')
        )
    )
    def calculate_base_value_villa(self, size, neighborhood):
        self.adjustments.append(("Villa setting ", 0.25))
        self.base_value = size * NEIGHBORHOOD_PRICES.get(neighborhood, 0) * 1.25
    @Rule(
        AND(
            Property(size=MATCH.size, neighborhood=MATCH.neighborhood),
            Property(pty_type='duplex')
        )
    )
    def calculate_base_value_duplex(self, size, neighborhood):
        self.adjustments.append(("Duplex setting ", 0.15))
        
        self.base_value = size * NEIGHBORHOOD_PRICES.get(neighborhood, 0) * 1.15
        
    @Rule(
        AND(
            Property(size=MATCH.size, neighborhood=MATCH.neighborhood),
            Property(pty_type='commercial',artery='primary')
        )
    )
    def calculate_base_value_commercial(self, size, neighborhood):
        self.adjustments.append(("Primary commercial artery ", 0.4))
        
        self.base_value = size * NEIGHBORHOOD_PRICES.get(neighborhood, 0) * 1.4 
    @Rule(
        AND(
            Property(size=MATCH.size, neighborhood=MATCH.neighborhood),
            Property(pty_type='commercial',artery='secondary')
        )
    )
    def calculate_base_value_commercial_secondary(self, size, neighborhood):
        self.adjustments.append(("Secondary commercial artery ", 0.3))
        
        self.base_value = size * NEIGHBORHOOD_PRICES.get(neighborhood, 0) * 1.3
        
    @Rule(
        AND(
            Property(size=MATCH.size, neighborhood=MATCH.neighborhood),
            Property(pty_type='office',artery='primary')
        )
    )
    def calculate_base_value_office_primary(self, size, neighborhood):
        self.adjustments.append(("Office - Primary artery ", 0.35))
        self.base_value = size * NEIGHBORHOOD_PRICES[neighborhood] * 1.35 
    
    @Rule(
        AND(
            Property(size=MATCH.size, neighborhood=MATCH.neighborhood),
            Property(pty_type='office',artery='secondary')
        )
    )
    def calculate_base_value_office_secondary(self, size, neighborhood):
        self.adjustments.append(("Office - Secondary artery ", 0.3))
        self.base_value = size * NEIGHBORHOOD_PRICES[neighborhood] * 1.3 

    def calculate_final_value(self):
        total_adjustment = sum(adj[1] for adj in self.adjustments) #sum of adjustments
        final_value = self.base_value * (1 + total_adjustment)
        
        return {
            "base_value": round(self.base_value, 2),
            "adjustments": self.adjustments,
            "total_adjustment_percentage": round(total_adjustment * 100, 2),
            "final_value": round(final_value, 2)
        }

def estimate_property_value(**kwargs):
    engine = PropertyValuationEngine()
    engine.reset()
    
    engine.declare(Property(**kwargs))
    
    engine.run()
    
    return engine.calculate_final_value()

# if __name__ == "__main__":
    result = estimate_property_value(
        size=120,
        rooms=4,
        bathrooms=1,
        parkings=0,
        condition='excellent',
        standing='high',
        pty_type='villa',
        market_demand=150,
        amenities=['air_conditioning', 'pool'],
        neighborhood='menzah 1',
        price_per_sqm=2000 
    )

    print("Property Valuation:")
    print(f"Base Value: {result['base_value']} TND")
    print("Adjustments:")
    for adj in result['adjustments']:
        print(f"- {adj[0]}: {adj[1]*100}%")
    print(f"Final Estimated Value: {result['final_value']} TND")