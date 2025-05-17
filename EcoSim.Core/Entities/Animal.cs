using EcoSim.Core.Entities;

namespace EcoSim.Core.Entities
{
    /// <summary>
    /// Shared logic for Herbivore & Carnivore.
    /// </summary>
    public abstract class Animal : Entity, IEdible
    {
        public int Hunger              { get; protected set; }
        public int ReproductionThreshold { get; }

        // When this animal is eaten, yields half its health
        public int FoodValue => Health / 2;

        protected Animal(int initialHealth, int lifespan, int reproductionThreshold)
            : base(initialHealth, lifespan)
        {
            Hunger = 0;
            ReproductionThreshold = reproductionThreshold;
        }

        public override void Update()
        {
            base.Update();
            if (IsDead) return;

            Hunger++;
            Health--;                // starve if not fed
            if (Hunger >= ReproductionThreshold)
                TryReproduce();

            Move();
        }

        /// <summary>
        /// Species‑specific movement logic.
        /// </summary>
        public abstract void Move();

        /// <summary>
        /// Species‑specific reproduction logic.
        /// </summary>
        protected abstract void TryReproduce();
    }
}
