import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { NavigationEnd, Router, RouterOutlet } from '@angular/router';
import { filter, map } from 'rxjs/operators';

import { Navbar } from './core/components/navbar/navbar';
import { I18nService } from './core/i18n/i18n.service';
import { ChatbotWidget } from './features/chatbot-widget/chatbot-widget';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, Navbar, ChatbotWidget],
  template: `
    @if (showPublicChrome()) {
      <app-navbar />
    }
    <main class="main-content">
      <router-outlet />
    </main>
    @if (showPublicChrome()) {
      <app-chatbot-widget />
    }
  `,
  styles: [`
    :host {
      display: flex;
      flex-direction: column;
      height: 100vh;
      overflow: hidden;
    }
    .main-content {
      flex: 1;
      overflow-y: auto;
      scroll-behavior: smooth;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AppComponent {
  private readonly router = inject(Router);
  private readonly i18n = inject(I18nService);

  readonly showPublicChrome = toSignal(
    this.router.events.pipe(
      filter((e): e is NavigationEnd => e instanceof NavigationEnd),
      map(() => !this.router.url.startsWith('/admin')),
    ),
    { initialValue: !this.router.url.startsWith('/admin') },
  );
}
