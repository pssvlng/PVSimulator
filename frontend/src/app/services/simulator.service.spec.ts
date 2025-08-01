import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { SimulatorService, SimulationData, SimulationResponse } from './simulator.service';

describe('SimulatorService', () => {
  let service: SimulatorService;
  let httpMock: HttpTestingController;

  const mockSimulationData: SimulationData[] = [
    { timestamp: '2025-07-31T12:00:00', meter: 5.5, pv: 7.2, net: 12.7 },
    { timestamp: '2025-07-31T12:00:03', meter: 6.1, pv: 7.1, net: 13.2 }
  ];

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [SimulatorService]
    });
    service = TestBed.inject(SimulatorService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should start simulation', () => {
    const mockResponse: SimulationResponse = { status: 'started', running: true };

    service.startSimulation().subscribe(response => {
      expect(response).toEqual(mockResponse);
    });

    const req = httpMock.expectOne('http://localhost:5000/start');
    expect(req.request.method).toBe('POST');
    req.flush(mockResponse);
  });

  it('should stop simulation', () => {
    const mockResponse: SimulationResponse = { status: 'stopped', running: false };

    service.stopSimulation().subscribe(response => {
      expect(response).toEqual(mockResponse);
    });

    const req = httpMock.expectOne('http://localhost:5000/stop');
    expect(req.request.method).toBe('POST');
    req.flush(mockResponse);
  });

  it('should get status', () => {
    const mockStatus = { running: true };

    service.getStatus().subscribe(status => {
      expect(status).toEqual(mockStatus);
    });

    const req = httpMock.expectOne('http://localhost:5000/status');
    expect(req.request.method).toBe('GET');
    req.flush(mockStatus);
  });

  it('should get results', () => {
    service.getResults().subscribe(data => {
      expect(data).toEqual(mockSimulationData);
      expect(data.length).toBe(2);
    });

    const req = httpMock.expectOne('http://localhost:5000/results');
    expect(req.request.method).toBe('GET');
    req.flush(mockSimulationData);
  });

  it('should get latest results', () => {
    service.getLatestResults().subscribe(data => {
      expect(data).toEqual(mockSimulationData);
    });

    const req = httpMock.expectOne('http://localhost:5000/results/latest');
    expect(req.request.method).toBe('GET');
    req.flush(mockSimulationData);
  });

  it('should update status', () => {
    let currentStatus = false;
    
    service.status$.subscribe(status => {
      currentStatus = status;
    });

    service.updateStatus(true);
    expect(currentStatus).toBe(true);

    service.updateStatus(false);
    expect(currentStatus).toBe(false);
  });

  it('should check initial status on construction', () => {
    const mockStatus = { running: true };
    
    // Create a new service instance to test constructor behavior
    const newService = new SimulatorService();
    
    // Simulate the HTTP call made in constructor
    const req = httpMock.expectOne('http://localhost:5000/status');
    expect(req.request.method).toBe('GET');
    req.flush(mockStatus);
    
    newService.status$.subscribe(status => {
      expect(status).toBe(true);
    });
  });

  it('should handle API errors gracefully', () => {
    spyOn(console, 'error');
    
    service.getStatus().subscribe({
      next: () => fail('should have failed'),
      error: (error) => {
        expect(error.status).toBe(500);
      }
    });

    const req = httpMock.expectOne('http://localhost:5000/status');
    req.flush('Server Error', { status: 500, statusText: 'Internal Server Error' });
  });

  it('should use correct API URLs for different environments', () => {
    // Test development environment (default)
    service.getStatus().subscribe();
    const devReq = httpMock.expectOne('http://localhost:5000/status');
    devReq.flush({ running: false });
    
    expect(devReq.request.url).toContain('http://localhost:5000');
  });
});
