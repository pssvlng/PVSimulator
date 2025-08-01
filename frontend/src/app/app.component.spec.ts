import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { of, throwError } from 'rxjs';
import { AppComponent } from './app.component';
import { SimulationData, SimulationResponse, SimulatorService } from './services/simulator.service';

describe('AppComponent', () => {
  let component: AppComponent;
  let fixture: ComponentFixture<AppComponent>;
  let simulatorService: jasmine.SpyObj<SimulatorService>;
  let httpMock: HttpTestingController;

  const mockSimulationData: SimulationData[] = [
    { timestamp: '2025-07-31T12:00:00', meter: 5.5, pv: 7.2, net: 1.7 },
    { timestamp: '2025-07-31T12:00:03', meter: 6.1, pv: 7.1, net: 1.0 }
  ];

  const mockResponse: SimulationResponse = { status: 'started', running: true };

  beforeEach(async () => {
    const simulatorSpy = jasmine.createSpyObj('SimulatorService', [
      'startSimulation',
      'stopSimulation',
      'getResults',
      'getLatestResults',
      'getStatus',
      'updateStatus'
    ], {
      status$: of(false)
    });

    await TestBed.configureTestingModule({
      imports: [RouterTestingModule, HttpClientTestingModule],
      declarations: [AppComponent],
      providers: [
        { provide: SimulatorService, useValue: simulatorSpy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(AppComponent);
    component = fixture.componentInstance;
    simulatorService = TestBed.inject(SimulatorService) as jasmine.SpyObj<SimulatorService>;
    httpMock = TestBed.inject(HttpTestingController);

    // Setup default spies
    simulatorService.getResults.and.returnValue(of([]));
    simulatorService.getLatestResults.and.returnValue(of([]));
    simulatorService.getStatus.and.returnValue(of({ running: false }));
    simulatorService.startSimulation.and.returnValue(of(mockResponse));
    simulatorService.stopSimulation.and.returnValue(of({ status: 'stopped', running: false }));
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should create the app', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize with correct default values', () => {
    expect(component.isRunning).toBeFalse();
    expect(component.chartData).toEqual([]);
    expect(component.latestData).toBeNull();
    expect(component.error).toBeNull();
  });

  it('should load initial data on ngOnInit', () => {
    simulatorService.getResults.and.returnValue(of(mockSimulationData));
    
    component.ngOnInit();
    
    expect(simulatorService.getResults).toHaveBeenCalled();
    expect(component.chartData).toEqual(mockSimulationData);
  });

  it('should start simulation when startSimulation is called', () => {
    component.startSimulation();
    
    expect(simulatorService.startSimulation).toHaveBeenCalled();
  });

  it('should stop simulation when stopSimulation is called', () => {
    component.stopSimulation();
    
    expect(simulatorService.stopSimulation).toHaveBeenCalled();
  });

  it('should handle start simulation error', () => {
    simulatorService.startSimulation.and.returnValue(throwError(() => new Error('Connection failed')));
    spyOn(console, 'error');
    
    component.startSimulation();
    
    expect(component.error).toContain('Failed to start simulation');
    expect(console.error).toHaveBeenCalled();
  });

  it('should handle stop simulation error', () => {
    simulatorService.stopSimulation.and.returnValue(throwError(() => new Error('Connection failed')));
    spyOn(console, 'error');
    
    component.stopSimulation();
    
    expect(component.error).toContain('Failed to stop simulation');
    expect(console.error).toHaveBeenCalled();
  });

  it('should handle empty chart data gracefully', () => {
    simulatorService.getResults.and.returnValue(of([]));
    
    component.ngOnInit();
    
    expect(component.chartData).toEqual([]);
  });
});
