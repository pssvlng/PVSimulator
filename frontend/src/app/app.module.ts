import { HttpClientModule } from '@angular/common/http';
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
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
    AppRoutingModule,
    HttpClientModule
  ],
  providers: [
    SimulatorService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
