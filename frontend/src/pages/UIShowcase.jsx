import {
  AlertTriangle,
  CheckCircle2,
  Clock3,
  ShieldCheck,
  TrendingUp,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";

function UIShowcase() {
  return (
    <div className="min-h-screen bg-background p-8 text-foreground">
      <div className="mx-auto max-w-7xl space-y-8">
        {/* Header */}
        <div>
          <div className="mb-2 text-sm font-semibold uppercase tracking-wider text-primary">
            TANGLE Design System
          </div>

          <h1 className="text-3xl font-semibold tracking-tight">
            Enterprise UI Foundation
          </h1>

          <p className="mt-2 max-w-2xl text-muted-foreground">
            Reusable components for transaction monitoring, anomaly
            investigation, risk assessment and governance workflows.
          </p>
        </div>

        <Separator />

        {/* Buttons */}
        <Card>
          <CardHeader>
            <CardTitle>Buttons</CardTitle>
            <CardDescription>
              Primary actions and secondary interface controls.
            </CardDescription>
          </CardHeader>

          <CardContent className="flex flex-wrap gap-3">
            <Button>
              Investigate Case
            </Button>

            <Button variant="secondary">
              View Details
            </Button>

            <Button variant="outline">
              Export Report
            </Button>

            <Button variant="ghost">
              Cancel
            </Button>

            <Button variant="destructive">
              Reject Case
            </Button>
          </CardContent>
        </Card>

        {/* Status badges */}
        <Card>
          <CardHeader>
            <CardTitle>Status & Risk</CardTitle>
            <CardDescription>
              Consistent visual language for case and risk states.
            </CardDescription>
          </CardHeader>

          <CardContent className="flex flex-wrap gap-3">
            <Badge>Primary</Badge>

            <Badge variant="secondary">
              Pending
            </Badge>

            <Badge variant="success">
              Approved
            </Badge>

            <Badge variant="warning">
              High Risk
            </Badge>

            <Badge variant="danger">
              Critical
            </Badge>

            <Badge variant="outline">
              Open
            </Badge>
          </CardContent>
        </Card>

        {/* KPI cards */}
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    Total Cases
                  </p>

                  <p className="mt-2 text-3xl font-semibold">
                    202
                  </p>

                  <p className="mt-1 text-xs text-muted-foreground">
                    Active monitoring population
                  </p>
                </div>

                <div className="rounded-lg bg-primary/10 p-2.5 text-primary">
                  <ShieldCheck className="h-5 w-5" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    Critical Cases
                  </p>

                  <p className="mt-2 text-3xl font-semibold text-danger">
                    65
                  </p>

                  <p className="mt-1 text-xs text-muted-foreground">
                    Require immediate attention
                  </p>
                </div>

                <div className="rounded-lg bg-danger/10 p-2.5 text-danger">
                  <AlertTriangle className="h-5 w-5" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    Payment Coverage
                  </p>

                  <p className="mt-2 text-3xl font-semibold">
                    91.27%
                  </p>

                  <p className="mt-1 flex items-center gap-1 text-xs text-success">
                    <TrendingUp className="h-3.5 w-3.5" />
                    Reconciliation metric
                  </p>
                </div>

                <div className="rounded-lg bg-success/10 p-2.5 text-success">
                  <CheckCircle2 className="h-5 w-5" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    Human Review
                  </p>

                  <p className="mt-2 text-3xl font-semibold">
                    197
                  </p>

                  <p className="mt-1 flex items-center gap-1 text-xs text-warning">
                    <Clock3 className="h-3.5 w-3.5" />
                    Pending review
                  </p>
                </div>

                <div className="rounded-lg bg-warning/10 p-2.5 text-warning">
                  <Clock3 className="h-5 w-5" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Form */}
        <Card>
          <CardHeader>
            <CardTitle>Form Controls</CardTitle>
            <CardDescription>
              Standardized inputs for investigation and governance workflows.
            </CardDescription>
          </CardHeader>

          <CardContent className="grid gap-5 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="case-id">
                Case ID
              </Label>

              <Input
                id="case-id"
                placeholder="CASE-0095"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="transaction-id">
                Transaction ID
              </Label>

              <Input
                id="transaction-id"
                placeholder="TXN-2026-0001"
              />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default UIShowcase;