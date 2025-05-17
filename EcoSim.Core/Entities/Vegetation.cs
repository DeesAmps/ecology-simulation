using System;

namespace EcoSim.Core.Entities
{
    /// <summary>
    /// Static plant that regrows and can be eaten.
    /// </summary>
    public class Vegetation : Entity, IEdible
    {
        private readonly int _maxHealth;
        private readonly Random _rng = new();

        public int FoodValue    { get; private set; }
        public int RegrowthRate { get; }

        public Vegetation(int initialHealth, int lifespan, int foodValue, int regrowthRate)
            : base(initialHealth, lifespan)
        {
            _maxHealth    = initialHealth;
            FoodValue     = foodValue;
            RegrowthRate  = regrowthRate;  // e.g. probability% to regrow 1hp each tick
        }

        public override void Update()
        {
            base.Update();
            if (IsDead) return;

            // passive regrowth
            if (Health < _maxHealth && _rng.NextDouble() < RegrowthRate / 100.0)
                Health++;
        }

        /// <summary>
        /// Called by animal when they eat this plant.
        /// </summary>
        public void BeEaten(int amount)
        {
            Health = Math.Max(0, Health - amount);
            if (Health == 0) IsDead = true;
        }
    }
}
