import { Routes } from '@angular/router';

import { adminAuthGuard, adminGuestGuard } from '../../core/guards/admin-auth.guard';

export const adminRoutes: Routes = [
  {
    path: 'login',
    canActivate: [adminGuestGuard],
    loadComponent: () =>
      import('./login/admin-login.component').then((m) => m.AdminLoginComponent),
  },
  {
    path: '',
    loadComponent: () =>
      import('./layout/admin-layout.component').then(
        (m) => m.AdminLayoutComponent,
      ),
    canActivate: [adminAuthGuard],
    children: [
      { path: '', redirectTo: 'department', pathMatch: 'full' },
      {
        path: 'department',
        loadComponent: () =>
          import('./department-list/department-list.component').then(
            (m) => m.DepartmentListComponent,
          ),
      },
      {
        path: 'department/new',
        loadComponent: () =>
          import('./department-form/department-form.component').then(
            (m) => m.DepartmentFormComponent,
          ),
        data: { departmentFormMode: 'create' as const },
      },
      {
        path: 'department/:departmentId/edit',
        loadComponent: () =>
          import('./department-form/department-form.component').then(
            (m) => m.DepartmentFormComponent,
          ),
        data: { departmentFormMode: 'edit' as const },
      },
      {
        path: 'department/:departmentId',
        loadComponent: () =>
          import('./department-detail/department-detail.component').then(
            (m) => m.DepartmentDetailComponent,
          ),
      },
      {
        path: 'doctors',
        loadComponent: () =>
          import('./doctor-list/doctor-list.component').then(
            (m) => m.DoctorListComponent,
          ),
      },
      {
        path: 'knowledge-base',
        loadComponent: () =>
          import('./knowledge-base/kb-list/kb-list.component').then(
            (m) => m.KbListComponent,
          ),
      },
      {
        path: 'department/:departmentId/doctor/:doctorId',
        loadComponent: () =>
          import('./doctor-detail/doctor-detail.component').then(
            (m) => m.DoctorDetailComponent,
          ),
      },
    ],
  },
];
