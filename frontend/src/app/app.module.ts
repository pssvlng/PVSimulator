import { HttpClientModule } from '@angular/common/http';
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppComponent } from './app.component';
import { ChartComponent } from './components/chart/chart.component';
import { ControlComponent } from './components/control/control.component';
import { SimulatorService } from './services/simulator.service';

@NgModule({
  declarations: [
    AppComponent,
    ControlComponent,
    ChartComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule
  ],
  providers: [
    SimulatorService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
