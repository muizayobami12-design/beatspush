'use client';

import { Users, Crown } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import type { FanClub } from '@/services/fanClubService';

interface FanClubCardProps {
  club: FanClub;
}

export function FanClubCard({ club }: FanClubCardProps) {
  return (
    <Link href={`/fan-clubs/${club.id}`}>
      <div className="bg-card rounded-lg border hover:border-primary/50 transition-all hover:shadow-md overflow-hidden group">
        {/* Cover Image */}
        <div className="relative h-40 bg-gradient-to-br from-primary/20 to-purple-500/20">
          {club.cover_image_url ? (
            <img
              src={club.cover_image_url}
              alt={club.name}
              className="w-full h-full object-cover transition-transform group-hover:scale-105"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <Crown className="h-16 w-16 text-muted-foreground opacity-30" />
            </div>
          )}
          
          {club.is_member && (
            <div className="absolute top-3 right-3 px-2 py-1 rounded-full bg-green-500 text-white text-xs font-medium">
              Member
            </div>
          )}
        </div>

        <div className="p-4">
          {/* Club Name */}
          <h3 className="text-lg font-bold mb-1 line-clamp-1 group-hover:text-primary transition-colors">
            {club.name}
          </h3>
          
          {/* Artist Name */}
          <p className="text-sm text-muted-foreground mb-3">
            by {club.artist_name}
          </p>

          {/* Description */}
          <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
            {club.description}
          </p>

          {/* Member Count */}
          <div className="flex items-center justify-between pt-4 border-t">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Users className="h-4 w-4" />
              <span className="text-sm">
                {club.member_count.toLocaleString()} member{club.member_count !== 1 ? 's' : ''}
              </span>
            </div>
            
            <Button size="sm" variant={club.is_member ? 'outline' : 'default'}>
              {club.is_member ? 'View' : 'Join'}
            </Button>
          </div>
        </div>
      </div>
    </Link>
  );
}
