import React from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Star } from 'lucide-react';

export function Testimonials() {
  return (
    <section id="testimonials" className="container mx-auto px-4 py-16">
      <div className="mx-auto max-w-4xl text-center">
        <h2 className="mb-4 text-3xl font-bold text-foreground">Loved by designers and everyday users</h2>
        <p className="mb-8 text-muted-foreground">Real feedback about how Clazzy helps people look their best.</p>

        <div className="grid gap-6 md:grid-cols-3">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Star className="h-5 w-5 text-yellow-400" />
                <span className="text-sm font-medium">Product Designer</span>
              </div>
              <CardTitle>"Fast, thoughtful suggestions"</CardTitle>
              <CardDescription>Clazzy suggests outfits that actually match my style.</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">The color recommendations are especially helpful when styling clients.</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Star className="h-5 w-5 text-yellow-400" />
                <span className="text-sm font-medium">Stylist</span>
              </div>
              <CardTitle>"Saves me time"</CardTitle>
              <CardDescription>Outfit generation for occasions is a game changer.</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">I can quickly iterate through looks before sending to clients.</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Star className="h-5 w-5 text-yellow-400" />
                <span className="text-sm font-medium">Everyday User</span>
              </div>
              <CardTitle>"I actually wear more outfits"</CardTitle>
              <CardDescription>Clazzy made my wardrobe feel new again.</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Super easy to use and fun to explore.</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  );
}

export function Pricing() {
  return (
    <section id="pricing" className="container mx-auto px-4 py-16 bg-transparent">
      <div className="mx-auto max-w-5xl text-center">
        <h2 className="mb-4 text-3xl font-bold text-foreground">Simple pricing</h2>
        <p className="mb-8 text-muted-foreground">One plan to get started — scale as you grow.</p>

        <div className="grid gap-6 md:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle>Free</CardTitle>
              <CardDescription>Personal use, limited uploads</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-4 text-2xl font-bold text-foreground">$0</div>
              <Button variant="outline">Get started</Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Pro</CardTitle>
              <CardDescription>Everything you need for daily styling</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-4 text-2xl font-bold text-foreground">$9 / mo</div>
              <Button>Start trial</Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Teams</CardTitle>
              <CardDescription>Collaborate across multiple wardrobes</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-4 text-2xl font-bold text-foreground">Contact us</div>
              <Button variant="outline">Contact sales</Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  );
}

export default function Marketing() {
  return (
    <>
      <Testimonials />
      <Pricing />
    </>
  );
}
