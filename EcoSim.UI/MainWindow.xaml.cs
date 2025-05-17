using System;
using System.Windows;
using System.Windows.Shapes;
using System.Windows.Threading;
using EcoSim.Core;
using EcoSim.Core.Entities;
using System.Windows.Media;

namespace EcoSim.UI
{
    public partial class MainWindow : Window
    {
        private readonly Simulation _sim;
        private readonly DispatcherTimer _timer;
        private const int CellSize = 10;

        public MainWindow()
        {
            InitializeComponent();

            _sim = new Simulation(width: 50, height: 50);

            _timer = new DispatcherTimer
            {
                Interval = TimeSpan.FromMilliseconds(200)
            };
            _timer.Tick += OnTick;
            _timer.Start();
        }

        private void OnTick(object sender, EventArgs e)
        {
            _sim.Tick();
            RenderEntities();
        }

        private void RenderEntities()
        {
            WorldCanvas.Children.Clear();

            foreach (var ent in _sim.Entities)
            {
                var rect = new Rectangle
                {
                    Width  = CellSize,
                    Height = CellSize,
                    Fill   = ent switch
                    {
                        Herbivore _ => Brushes.Blue,
                        Carnivore _ => Brushes.Red,
                        Vegetation _ => Brushes.Green,
                        _            => Brushes.Gray
                    }
                };

                Canvas.SetLeft(rect, ent.X * CellSize);
                Canvas.SetTop( rect, ent.Y * CellSize);
                WorldCanvas.Children.Add(rect);
            }
        }
    }
}
