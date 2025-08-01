import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ChartComponent } from './chart.component';
import { SimulationData } from '../../services/simulator.service';

describe('ChartComponent', () => {
  let component: ChartComponent;
  let fixture: ComponentFixture<ChartComponent>;

  const mockData: SimulationData[] = [
    { timestamp: '2025-07-31T12:00:00', meter: 5.5, pv: 7.2, net: 1.7 },
    { timestamp: '2025-07-31T12:00:03', meter: 6.1, pv: 7.1, net: 1.0 },
    { timestamp: '2025-07-31T12:00:06', meter: 4.8, pv: 7.0, net: 2.2 }
  ];

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ChartComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(ChartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize with empty data', () => {
    expect(component.data).toEqual([]);
  });

  it('should accept data input', () => {
    component.data = mockData;
    expect(component.data).toEqual(mockData);
    expect(component.data.length).toBe(3);
  });

  it('should handle empty data gracefully', () => {
    component.data = [];
    expect(component.data).toEqual([]);
  });

  it('should handle data with correct properties', () => {
    component.data = mockData;
    expect(mockData[0].meter).toBeDefined();
    expect(mockData[0].pv).toBeDefined();
    expect(mockData[0].net).toBeDefined();
    expect(mockData[0].timestamp).toBeDefined();
  });
});
